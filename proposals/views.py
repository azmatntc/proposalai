import logging
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import StandardResultsSetPagination

from .models import Proposal, ProposalTemplate 
from .serializers import (
    ProposalSerializer, ProposalListSerializer,
    ProposalTemplateSerializer
)
from .filters import ProposalFilter, ProposalTemplateFilter

logger = logging.getLogger(__name__)


class ProposalViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filterset_class = ProposalFilter
    ordering_fields = ['created_at', 'updated_at', 'status', 'client_name', 'word_count', 'rating']
    ordering = ['-created_at']
    search_fields = ['title', 'client_name', 'client_company', 'job_description']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProposalListSerializer
        return ProposalSerializer

    def get_queryset(self):
        return Proposal.objects.filter(
            user=self.request.user,
            is_active=True,
            deleted_at__isnull=True,
        ).select_related('template').prefetch_related('leads')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Trigger AI proposal generation."""
        proposal = self.get_object()

        if request.user.has_reached_quota():
            return Response({
                'error': 'Monthly quota exceeded.',
                'remaining': request.user.get_remaining_quota(),
                'upgrade_url': '/upgrade',
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        if not proposal.job_description:
            return Response({'error': 'Job description is required for AI generation.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from .tasks import generate_proposal_ai
            task = generate_proposal_ai.delay(str(proposal.id))
            return Response({
                'task_id': task.id,
                'status': 'processing',
                'estimated_time': '10-30 seconds',
                'poll_url': f'/api/v1/proposals/{proposal.id}/generation-status/',
            }, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.error(f"Failed to queue generation task: {e}")
            return Response({'error': 'Failed to start generation. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'], url_path='generation-status')
    def generation_status(self, request, pk=None):
        """Poll for generation task status."""
        from celery.result import AsyncResult
        task_id = request.query_params.get('task_id')
        if not task_id:
            proposal = self.get_object()
            return Response({
                'proposal_id': str(proposal.id),
                'status': proposal.status,
                'word_count': proposal.word_count,
            })
        result = AsyncResult(task_id)
        return Response({'task_id': task_id, 'status': result.status, 'result': result.result if result.ready() else None})

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Clone a proposal."""
        original = self.get_object()
        new_proposal = original.duplicate()
        serializer = ProposalSerializer(new_proposal, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """Toggle favorite status."""
        proposal = self.get_object()
        proposal.is_favorite = not proposal.is_favorite
        proposal.save(update_fields=['is_favorite'])
        return Response({'is_favorite': proposal.is_favorite})

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Mark proposal as sent."""
        proposal = self.get_object()
        if proposal.status not in ['draft', 'generated', 'edited']:
            return Response({'error': f'Cannot send proposal with status: {proposal.status}'}, status=status.HTTP_400_BAD_REQUEST)

        proposal.status = 'sent'
        proposal.sent_at = timezone.now()
        proposal.folder = 'sent'
        proposal.save(update_fields=['status', 'sent_at', 'folder'])

        # Log activity for linked leads
        from leads.models import LeadActivity
        for lead in proposal.leads.all():
            LeadActivity.objects.create(
                lead=lead, user=request.user,
                activity_type='proposal_sent',
                description=f'Proposal "{proposal.title}" sent',
                metadata={'proposal_id': str(proposal.id)},
                is_system_generated=True,
            )

        return Response(ProposalSerializer(proposal, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Proposal analytics."""
        qs = self.get_queryset()
        now = timezone.now()

        by_status = dict(
            qs.values('status').annotate(count=Count('id')).values_list('status', 'count')
        )
        total = qs.count()
        accepted = by_status.get('accepted', 0)

        return Response({
            'total': total,
            'by_status': by_status,
            'this_month': qs.filter(created_at__year=now.year, created_at__month=now.month).count(),
            'acceptance_rate': round((accepted / total * 100), 1) if total > 0 else 0,
            'avg_generation_time_ms': qs.filter(generation_time_ms__gt=0).aggregate(
                avg=Avg('generation_time_ms')
            )['avg'] or 0,
            'total_ai_cost_usd': float(qs.aggregate(total=Sum('ai_cost_usd'))['total'] or 0),
            'favorites': qs.filter(is_favorite=True).count(),
            'quota': {
                'used': request.user.proposals_generated_this_month,
                'total': request.user.monthly_proposal_quota,
                'remaining': request.user.get_remaining_quota(),
            },
        })


class ProposalTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ProposalTemplateSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filterset_class = ProposalTemplateFilter
    ordering_fields = ['created_at', 'usage_count', 'average_rating', 'name']
    ordering = ['-is_favorite', '-usage_count']
    search_fields = ['name', 'description']

    def get_queryset(self):
        user = self.request.user
        return ProposalTemplate.objects.filter(
            Q(user=user) | Q(is_system_template=True) | Q(is_public=True),
            is_active=True,
            deleted_at__isnull=True,
        ).select_related('user')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_system_template:
            return Response({'error': 'System templates cannot be deleted.'}, status=status.HTTP_403_FORBIDDEN)
        from django.utils import timezone as tz
        instance.deleted_at = tz.now()
        instance.is_active = False
        instance.save(update_fields=['deleted_at', 'is_active'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        """Clone a template for the current user."""
        template = self.get_object()
        new_template = template.clone_for_user(request.user)
        return Response(ProposalTemplateSerializer(new_template, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Increment usage count and return template structure."""
        template = self.get_object()
        template.increment_usage()
        return Response({
            'id': str(template.id),
            'name': template.name,
            'structure': template.structure,
            'default_variables': template.default_variables,
            'tone': template.tone,
        })

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """List categories with counts."""
        from .models import CATEGORY_CHOICES
        qs = self.get_queryset()
        counts = dict(qs.values('category').annotate(count=Count('id')).values_list('category', 'count'))
        return Response([
            {'value': k, 'label': v, 'count': counts.get(k, 0)}
            for k, v in CATEGORY_CHOICES
        ])
