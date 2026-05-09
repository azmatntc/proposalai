import logging
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import StandardResultsSetPagination
from .models import Lead, LeadActivity, LeadScore
from .serializers import LeadSerializer, LeadListSerializer, LeadActivitySerializer, LeadScoreSerializer
from .filters import LeadFilter
from .scoring import LeadScoringService

logger = logging.getLogger(__name__)


class LeadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filterset_class = LeadFilter
    ordering_fields = ['created_at', 'updated_at', 'status', 'priority',
                       'estimated_value', 'next_follow_up_at', 'last_contact_at']
    ordering = ['-created_at']
    search_fields = ['first_name', 'last_name', 'email', 'company', 'notes']

    def get_serializer_class(self):
        if self.action == 'list':
            return LeadListSerializer
        return LeadSerializer

    def get_queryset(self):
        return Lead.objects.filter(
            user=self.request.user,
            is_active=True,
            deleted_at__isnull=True,
        ).select_related('score', 'assigned_to').prefetch_related('activities', 'proposals')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ── Activities ──────────────────────────────────────────────────────────────

    @action(detail=True, methods=['get', 'post'])
    def activities(self, request, pk=None):
        lead = self.get_object()
        if request.method == 'GET':
            activities = lead.activities.select_related('user').order_by('-created_at')
            page = self.paginate_queryset(activities)
            serializer = LeadActivitySerializer(page or activities, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data) if page else Response(serializer.data)

        serializer = LeadActivitySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        activity = serializer.save(lead=lead, user=request.user)
        lead.update_last_contact()
        return Response(LeadActivitySerializer(activity, context={'request': request}).data, status=status.HTTP_201_CREATED)

    # ── Score ────────────────────────────────────────────────────────────────────

    @action(detail=True, methods=['get'])
    def score(self, request, pk=None):
        lead = self.get_object()
        score, _ = LeadScore.objects.get_or_create(lead=lead, defaults={'user': request.user})
        return Response(LeadScoreSerializer(score).data)

    @action(detail=True, methods=['post'], url_path='score/recalc')
    def score_recalc(self, request, pk=None):
        lead = self.get_object()
        score = LeadScoringService.recalculate_score(str(lead.id))
        if not score:
            return Response({'error': 'Score calculation failed.'}, status=500)
        return Response(LeadScoreSerializer(score).data)

    # ── Status transitions ───────────────────────────────────────────────────────

    @action(detail=True, methods=['post'])
    def convert(self, request, pk=None):
        lead = self.get_object()
        old_status = lead.status
        lead.status = 'closed_won'
        lead.actual_close_date = timezone.now().date()
        lead.probability = 100
        lead.save(update_fields=['status', 'actual_close_date', 'probability'])

        LeadActivity.objects.create(
            lead=lead, user=request.user,
            activity_type='status_changed',
            description=f'Lead converted: {old_status} → closed_won',
            metadata={'old_status': old_status, 'new_status': 'closed_won'},
            is_system_generated=True,
        )
        return Response(LeadSerializer(lead, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def disqualify(self, request, pk=None):
        lead = self.get_object()
        reason = request.data.get('reason', '')
        old_status = lead.status
        lead.status = 'disqualified'
        lead.close_reason = reason
        lead.save(update_fields=['status', 'close_reason'])

        LeadActivity.objects.create(
            lead=lead, user=request.user,
            activity_type='status_changed',
            description=f'Lead disqualified. Reason: {reason}',
            metadata={'old_status': old_status, 'reason': reason},
            is_system_generated=True,
        )
        return Response(LeadSerializer(lead, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def follow_up(self, request, pk=None):
        lead = self.get_object()
        follow_up_at = request.data.get('follow_up_at')
        note = request.data.get('note', '')

        if not follow_up_at:
            return Response({'error': 'follow_up_at is required.'}, status=400)

        lead.next_follow_up_at = follow_up_at
        lead.save(update_fields=['next_follow_up_at'])

        LeadActivity.objects.create(
            lead=lead, user=request.user,
            activity_type='follow_up_set',
            description=f'Follow-up set for {follow_up_at}. {note}',
            metadata={'follow_up_at': str(follow_up_at), 'note': note},
        )
        return Response({'next_follow_up_at': str(lead.next_follow_up_at)})

    # ── Bulk operations ──────────────────────────────────────────────────────────

    @action(detail=False, methods=['post'], url_path='bulk-update')
    def bulk_update(self, request):
        lead_ids = request.data.get('lead_ids', [])
        updates = request.data.get('updates', {})

        ALLOWED_BULK_FIELDS = {'status', 'priority', 'assigned_to_id', 'is_hot'}
        safe_updates = {k: v for k, v in updates.items() if k in ALLOWED_BULK_FIELDS}

        if not safe_updates:
            return Response({'error': 'No valid fields to update.'}, status=400)

        leads = self.get_queryset().filter(id__in=lead_ids)
        count = leads.count()
        leads.update(**safe_updates, updated_at=timezone.now())

        for lead in leads:
            LeadActivity.objects.create(
                lead=lead, user=request.user,
                activity_type='status_changed',
                description=f'Bulk updated: {list(safe_updates.keys())}',
                metadata={'updates': safe_updates},
                is_system_generated=True,
            )

        return Response({'updated': count, 'fields': list(safe_updates.keys())})

    # ── Analytics ────────────────────────────────────────────────────────────────

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        now = timezone.now()

        by_status = dict(qs.values('status').annotate(c=Count('id')).values_list('status', 'c'))
        by_source = dict(qs.values('source').annotate(c=Count('id')).values_list('source', 'c'))
        by_score_tier = dict(
            qs.exclude(score__isnull=True)
              .values('score__score_tier')
              .annotate(c=Count('id'))
              .values_list('score__score_tier', 'c')
        )

        pipeline_value = qs.exclude(
            status__in=['closed_won', 'closed_lost', 'disqualified']
        ).aggregate(total=Sum('estimated_value'))['total'] or 0

        won = by_status.get('closed_won', 0)
        total_closed = won + by_status.get('closed_lost', 0)

        follow_up_overdue = qs.filter(
            next_follow_up_at__lt=now,
            next_follow_up_at__isnull=False,
        ).count()

        return Response({
            'total': qs.count(),
            'by_status': by_status,
            'by_source': by_source,
            'by_score_tier': by_score_tier,
            'pipeline_value': float(pipeline_value),
            'conversion_rate': round(won / total_closed * 100, 1) if total_closed > 0 else 0,
            'follow_up_overdue': follow_up_overdue,
            'hot_leads': qs.filter(is_hot=True).count(),
            'this_month': qs.filter(created_at__year=now.year, created_at__month=now.month).count(),
            'avg_estimated_value': float(qs.exclude(estimated_value__isnull=True).aggregate(avg=Avg('estimated_value'))['avg'] or 0),
        })

    # ── Import / Export ──────────────────────────────────────────────────────────

    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file uploaded.'}, status=400)

        import csv, io
        file = request.FILES['file']
        decoded = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))

        created, skipped, errors = 0, 0, []
        for i, row in enumerate(reader, 1):
            try:
                email = row.get('email', '').strip().lower()
                if not email:
                    errors.append(f"Row {i}: email required")
                    continue

                lead, was_created = Lead.objects.get_or_create(
                    user=request.user,
                    email=email,
                    deleted_at__isnull=True,
                    defaults={
                        'first_name': row.get('first_name', '').strip(),
                        'last_name': row.get('last_name', '').strip(),
                        'company': row.get('company', '').strip(),
                        'phone': row.get('phone', '').strip(),
                        'source': 'other',
                    }
                )
                if was_created:
                    created += 1
                else:
                    skipped += 1
            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")

        return Response({'created': created, 'skipped': skipped, 'errors': errors})

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        import csv
        from django.http import HttpResponse

        qs = self.get_queryset()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="leads.csv"'

        writer = csv.writer(response)
        writer.writerow(['first_name', 'last_name', 'email', 'phone', 'company',
                         'job_title', 'status', 'priority', 'source',
                         'estimated_value', 'score', 'created_at'])
        for lead in qs:
            score = lead.score.total_score if hasattr(lead, 'score') else ''
            writer.writerow([
                lead.first_name, lead.last_name, lead.email, lead.phone,
                lead.company, lead.job_title, lead.status, lead.priority,
                lead.source, lead.estimated_value or '', score,
                lead.created_at.strftime('%Y-%m-%d'),
            ])
        return response
