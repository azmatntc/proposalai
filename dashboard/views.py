import logging
from datetime import timedelta
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        prev_month_start = (month_start - timedelta(days=1)).replace(day=1)

        from leads.models import Lead, LeadScore
        from proposals.models import Proposal

        leads_qs = Lead.objects.filter(user=user, is_active=True, deleted_at__isnull=True)
        proposals_qs = Proposal.objects.filter(user=user, is_active=True, deleted_at__isnull=True)

        # Core metrics
        total_leads = leads_qs.count()
        active_leads = leads_qs.exclude(status__in=['closed_won', 'closed_lost', 'disqualified']).count()
        closed_won = leads_qs.filter(status='closed_won').count()
        closed_total = leads_qs.filter(status__in=['closed_won', 'closed_lost']).count()
        conversion_rate = round(closed_won / closed_total * 100, 1) if closed_total > 0 else 0

        pipeline_value = leads_qs.exclude(
            status__in=['closed_won', 'closed_lost', 'disqualified']
        ).aggregate(v=Sum('estimated_value'))['v'] or 0

        # Month-over-month changes
        leads_this_month = leads_qs.filter(created_at__gte=month_start).count()
        leads_last_month = leads_qs.filter(created_at__gte=prev_month_start, created_at__lt=month_start).count()

        proposals_this_month = proposals_qs.filter(created_at__gte=month_start).count()
        proposals_accepted_this_month = proposals_qs.filter(
            status='accepted', accepted_at__gte=month_start
        ).count()

        follow_up_overdue = leads_qs.filter(
            next_follow_up_at__lt=now,
            next_follow_up_at__isnull=False,
        ).count()

        # Score distribution
        score_distribution = dict(
            LeadScore.objects.filter(user=user)
                .values('score_tier')
                .annotate(c=Count('id'))
                .values_list('score_tier', 'c')
        )

        return Response({
            'leads': {
                'total': total_leads,
                'active': active_leads,
                'this_month': leads_this_month,
                'last_month': leads_last_month,
                'mom_change': leads_this_month - leads_last_month,
            },
            'conversion': {
                'rate': conversion_rate,
                'closed_won': closed_won,
                'closed_total': closed_total,
            },
            'pipeline': {
                'value': float(pipeline_value),
                'currency': 'USD',
            },
            'proposals': {
                'generated': user.proposals_generated_this_month,
                'quota': user.monthly_proposal_quota,
                'remaining': user.get_remaining_quota(),
                'this_month': proposals_this_month,
                'accepted_this_month': proposals_accepted_this_month,
            },
            'follow_ups': {
                'overdue': follow_up_overdue,
            },
            'score_distribution': score_distribution,
        })


class DashboardActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from leads.models import LeadActivity
        limit = min(int(request.query_params.get('limit', 20)), 50)

        activities = LeadActivity.objects.filter(
            user=request.user
        ).select_related('lead').order_by('-created_at')[:limit]

        from leads.serializers import LeadActivitySerializer
        return Response(LeadActivitySerializer(activities, many=True, context={'request': request}).data)


class DashboardPipelineView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from leads.models import Lead

        stages = [
            ('new', 'New'), ('contacted', 'Contacted'), ('qualified', 'Qualified'),
            ('proposal_sent', 'Proposal Sent'), ('negotiating', 'Negotiating'),
        ]

        qs = Lead.objects.filter(user=request.user, is_active=True, deleted_at__isnull=True)
        pipeline = []
        for stage_value, stage_label in stages:
            stage_leads = qs.filter(status=stage_value)
            pipeline.append({
                'stage': stage_value,
                'label': stage_label,
                'count': stage_leads.count(),
                'value': float(stage_leads.aggregate(v=Sum('estimated_value'))['v'] or 0),
            })

        return Response({'stages': pipeline})


class DashboardRevenueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from leads.models import Lead
        from django.db.models.functions import TruncMonth
        import datetime

        now = timezone.now()
        six_months_ago = now - timedelta(days=180)

        monthly_revenue = (
            Lead.objects.filter(
                user=request.user,
                status='closed_won',
                actual_close_date__gte=six_months_ago.date(),
                estimated_value__isnull=False,
            )
            .annotate(month=TruncMonth('actual_close_date'))
            .values('month')
            .annotate(revenue=Sum('estimated_value'), count=Count('id'))
            .order_by('month')
        )

        return Response({
            'monthly': [
                {
                    'month': entry['month'].strftime('%Y-%m') if entry['month'] else None,
                    'revenue': float(entry['revenue'] or 0),
                    'count': entry['count'],
                }
                for entry in monthly_revenue
            ]
        })


class DashboardAIUsageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from analytics.models import AIUsageLog
        from django.db.models.functions import TruncDay

        now = timezone.now()
        thirty_ago = now - timedelta(days=30)

        logs = AIUsageLog.objects.filter(user=request.user, created_at__gte=thirty_ago)

        totals = logs.aggregate(
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('cost_usd'),
            total_requests=Count('id'),
            avg_latency=Avg('latency_ms'),
        )

        daily = (
            logs.annotate(day=TruncDay('created_at'))
                .values('day')
                .annotate(tokens=Sum('total_tokens'), cost=Sum('cost_usd'), requests=Count('id'))
                .order_by('day')
        )

        return Response({
            'totals': {
                'tokens': totals['total_tokens'] or 0,
                'cost_usd': float(totals['total_cost'] or 0),
                'requests': totals['total_requests'] or 0,
                'avg_latency_ms': round(totals['avg_latency'] or 0),
            },
            'daily': [
                {
                    'day': entry['day'].strftime('%Y-%m-%d'),
                    'tokens': entry['tokens'],
                    'cost_usd': float(entry['cost'] or 0),
                    'requests': entry['requests'],
                }
                for entry in daily
            ],
        })
