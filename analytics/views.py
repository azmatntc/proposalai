import logging
from datetime import timedelta

from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import StandardResultsSetPagination
from .models import AIUsageLog
from .serializers import AIUsageLogSerializer

logger = logging.getLogger(__name__)


class AIUsageListView(APIView):
    """GET /api/v1/analytics/ai-usage/ — paginated AI request log"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = AIUsageLog.objects.filter(user=request.user).select_related('proposal')
        if request.query_params.get('since'):
            qs = qs.filter(created_at__gte=request.query_params['since'])
        if request.query_params.get('model'):
            qs = qs.filter(model=request.query_params['model'])
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(AIUsageLogSerializer(page, many=True).data)


class AIUsageSummaryView(APIView):
    """GET /api/v1/analytics/ai-usage/summary/ — totals + daily breakdown"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        since = timezone.now() - timedelta(days=days)
        logs = AIUsageLog.objects.filter(user=request.user, created_at__gte=since)

        from django.db.models import Q
        totals = logs.aggregate(
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('cost_usd'),
            total_requests=Count('id'),
            avg_latency=Avg('latency_ms'),
            cached_requests=Count('id', filter=Q(was_cached=True)),
        )

        daily = list(
            logs.annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(tokens=Sum('total_tokens'), cost=Sum('cost_usd'), requests=Count('id'))
            .order_by('day')
        )

        return Response({
            'period_days': days,
            'totals': {
                'tokens':         totals['total_tokens'] or 0,
                'cost_usd':       float(totals['total_cost'] or 0),
                'requests':       totals['total_requests'] or 0,
                'avg_latency_ms': round(totals['avg_latency'] or 0),
                'cached_requests': totals['cached_requests'] or 0,
            },
            'daily': [
                {
                    'day':      e['day'].strftime('%Y-%m-%d'),
                    'tokens':   e['tokens'] or 0,
                    'cost_usd': float(e['cost'] or 0),
                    'requests': e['requests'],
                }
                for e in daily
            ],
        })


class AIUsageByModelView(APIView):
    """GET /api/v1/analytics/ai-usage/by-model/ — per-model breakdown"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        since = timezone.now() - timedelta(days=days)
        by_model = (
            AIUsageLog.objects
            .filter(user=request.user, created_at__gte=since)
            .values('model')
            .annotate(requests=Count('id'), tokens=Sum('total_tokens'),
                      cost=Sum('cost_usd'), avg_latency=Avg('latency_ms'))
            .order_by('-cost')
        )
        return Response([
            {
                'model':          e['model'],
                'requests':       e['requests'],
                'tokens':         e['tokens'] or 0,
                'cost_usd':       float(e['cost'] or 0),
                'avg_latency_ms': round(e['avg_latency'] or 0),
            }
            for e in by_model
        ])


class AnalyticsOverviewView(APIView):
    """
    GET /api/v1/analytics/overview/
    Single endpoint for the Analytics page — leads + proposals + revenue + AI usage.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        thirty_ago  = now - timedelta(days=30)
        six_months_ago = now - timedelta(days=180)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # ── Leads ─────────────────────────────────────────────
        from leads.models import Lead
        leads_qs = Lead.objects.filter(user=user, is_active=True, deleted_at__isnull=True)
        lead_by_status = dict(
            leads_qs.values('status').annotate(c=Count('id')).values_list('status', 'c')
        )
        lead_by_source = dict(
            leads_qs.values('source').annotate(c=Count('id')).values_list('source', 'c')
        )
        closed_won   = lead_by_status.get('closed_won', 0)
        closed_total = closed_won + lead_by_status.get('closed_lost', 0)
        pipeline_value = float(
            leads_qs.exclude(status__in=['closed_won', 'closed_lost', 'disqualified'])
            .aggregate(v=Sum('estimated_value'))['v'] or 0
        )

        # ── Proposals ─────────────────────────────────────────
        from proposals.models import Proposal
        props_qs = Proposal.objects.filter(user=user, is_active=True, deleted_at__isnull=True)
        prop_total     = props_qs.count()
        prop_by_status = dict(
            props_qs.values('status').annotate(c=Count('id')).values_list('status', 'c')
        )
        accepted       = prop_by_status.get('accepted', 0)
        total_ai_cost  = float(props_qs.aggregate(v=Sum('ai_cost_usd'))['v'] or 0)

        # ── Revenue monthly ───────────────────────────────────
        monthly_rev = list(
            leads_qs
            .filter(status='closed_won',
                    actual_close_date__gte=six_months_ago.date(),
                    estimated_value__isnull=False)
            .annotate(month=TruncMonth('actual_close_date'))
            .values('month')
            .annotate(revenue=Sum('estimated_value'), count=Count('id'))
            .order_by('month')
        )

        # ── AI usage ──────────────────────────────────────────
        ai_logs = AIUsageLog.objects.filter(user=user, created_at__gte=thirty_ago)
        ai_totals = ai_logs.aggregate(
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('cost_usd'),
            total_requests=Count('id'),
            avg_latency=Avg('latency_ms'),
        )
        ai_daily = list(
            ai_logs.annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(tokens=Sum('total_tokens'), cost=Sum('cost_usd'), requests=Count('id'))
            .order_by('day')
        )

        return Response({
            'leads': {
                'total':          leads_qs.count(),
                'this_month':     leads_qs.filter(created_at__gte=month_start).count(),
                'by_status':      lead_by_status,
                'by_source':      lead_by_source,
                'pipeline_value': pipeline_value,
                'conversion_rate': round(closed_won / closed_total * 100, 1) if closed_total else 0,
            },
            'proposals': {
                'total':              prop_total,
                'this_month':         props_qs.filter(created_at__gte=month_start).count(),
                'by_status':          prop_by_status,
                'acceptance_rate':    round(accepted / prop_total * 100, 1) if prop_total else 0,
                'total_ai_cost_usd':  total_ai_cost,
            },
            'revenue': {
                'monthly': [
                    {
                        'month':   e['month'].strftime('%Y-%m') if e['month'] else None,
                        'revenue': float(e['revenue'] or 0),
                        'count':   e['count'],
                    }
                    for e in monthly_rev
                ],
            },
            'ai_usage': {
                'totals': {
                    'tokens':         ai_totals['total_tokens']   or 0,
                    'cost_usd':       float(ai_totals['total_cost'] or 0),
                    'requests':       ai_totals['total_requests'] or 0,
                    'avg_latency_ms': round(ai_totals['avg_latency'] or 0),
                },
                'daily': [
                    {
                        'day':      e['day'].strftime('%Y-%m-%d'),
                        'tokens':   e['tokens']  or 0,
                        'cost_usd': float(e['cost'] or 0),
                        'requests': e['requests'],
                    }
                    for e in ai_daily
                ],
            },
        })