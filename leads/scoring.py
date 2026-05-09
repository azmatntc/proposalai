import logging
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count

logger = logging.getLogger(__name__)


class LeadScoringService:
    """
    Full lead scoring engine: engagement, recency, frequency, depth, demographic, intent.
    Supports real-time (per activity) and batch (nightly) recalculation.
    """

    RECENCY_THRESHOLDS = [1, 7, 30, 90]
    RECENCY_SCORES = [40, 30, 20, 10]

    @classmethod
    def recalculate_score(cls, lead_id: str):
        from .models import Lead, LeadScore
        try:
            lead = Lead.objects.select_related('score').get(id=lead_id)
        except Lead.DoesNotExist:
            logger.error(f"Lead {lead_id} not found for scoring")
            return None

        score, _ = LeadScore.objects.get_or_create(lead=lead, defaults={'user': lead.user})
        score.previous_score = score.total_score

        score.engagement_score = cls._engagement(lead, score)
        score.recency_score = cls._recency(lead, score)
        score.frequency_score = cls._frequency(lead, score)
        score.depth_score = cls._depth(lead, score)
        score.demographic_score = cls._demographic(lead, score)
        score.intent_score = cls._intent(lead, score)

        score.calculate_total_score()
        score.score_change = score.total_score - score.previous_score
        score.update_score_tier()
        score.record_history()
        score.save()

        if abs(score.score_change) >= 10:
            cls._notify_score_change(lead, score)

        return score

    @classmethod
    def _engagement(cls, lead, score) -> int:
        base = min(40, score.total_website_visits * 2)
        pages = min(20, score.total_pages_viewed)
        time_s = min(20, score.total_time_on_site_seconds // 60)
        email = min(10, score.email_opens_count + score.email_clicks_count * 2)
        proposal = min(10, score.proposal_views_count * 3 + score.proposal_time_spent_seconds // 30)
        return min(100, base + pages + time_s + email + proposal)

    @classmethod
    def _recency(cls, lead, score) -> int:
        now = timezone.now()
        val = 0
        if score.last_visit_at:
            days = (now - score.last_visit_at).days
            for i, threshold in enumerate(cls.RECENCY_THRESHOLDS):
                if days <= threshold:
                    val = max(val, cls.RECENCY_SCORES[i])
                    break
        if score.last_email_open_at:
            days = (now - score.last_email_open_at).days
            val += 15 if days <= 7 else (10 if days <= 30 else 0)
        if score.last_proposal_view_at:
            days = (now - score.last_proposal_view_at).days
            val += 20 if days <= 3 else (10 if days <= 14 else 0)
        return min(100, val)

    @classmethod
    def _frequency(cls, lead, score) -> int:
        from .models import LeadActivity
        now = timezone.now()
        thirty_ago = now - timedelta(days=30)

        visits = LeadActivity.objects.filter(lead=lead, activity_type='website_visit', created_at__gte=thirty_ago).count()
        emails = LeadActivity.objects.filter(lead=lead, activity_type__in=['email_opened', 'email_sent'], created_at__gte=thirty_ago).count()

        visits_score = min(30, int((visits / 4.33) * 10))
        emails_score = min(20, int((emails / 4.33) * 5))

        # Consistency: active weeks
        weekly_counts = []
        for week in range(4):
            ws = thirty_ago + timedelta(weeks=week)
            we = ws + timedelta(weeks=1)
            c = LeadActivity.objects.filter(lead=lead, created_at__range=(ws, we)).count()
            weekly_counts.append(c)

        active_weeks = sum(1 for c in weekly_counts if c > 0)
        consistency = 10 if active_weeks >= 3 else 0
        trend = 10 if len(weekly_counts) >= 2 and weekly_counts[-1] > weekly_counts[0] else 0

        return min(100, visits_score + emails_score + consistency + trend)

    @classmethod
    def _depth(cls, lead, score) -> int:
        visits = max(score.total_website_visits, 1)
        avg_time = score.total_time_on_site_seconds / visits
        avg_pages = score.total_pages_viewed / visits

        time_score = min(25, int(avg_time / 10))
        pages_score = min(25, int(avg_pages * 5))
        proposal_depth = min(25, score.proposal_time_spent_seconds // 60)
        downloads = min(15, score.content_downloads_count * 3)
        meeting_bonus = 10 if (score.calls_scheduled_count > 0 or score.meetings_attended_count > 0) else 0

        return min(100, time_score + pages_score + proposal_depth + downloads + meeting_bonus)

    @classmethod
    def _demographic(cls, lead, score) -> int:
        val = 0
        if lead.company: val += 15
        if lead.job_title: val += 15
        if lead.industry: val += 20
        if lead.company_size: val += 20
        if lead.website: val += 15
        if lead.linkedin_url: val += 15
        return min(100, val)

    @classmethod
    def _intent(cls, lead, score) -> int:
        from .models import LeadActivity
        now = timezone.now()
        recent = LeadActivity.objects.filter(lead=lead, created_at__gte=now - timedelta(days=30))
        activity_types = set(recent.values_list('activity_type', flat=True))

        val = 0
        if 'proposal_viewed' in activity_types: val += 30
        if 'form_submitted' in activity_types: val += 20
        if 'email_link_clicked' in activity_types or 'link_clicked' in activity_types: val += 15
        if 'meeting_scheduled' in activity_types: val += 10

        # Multiple visits in 24h
        visits_24h = LeadActivity.objects.filter(
            lead=lead, activity_type='website_visit', created_at__gte=now - timedelta(hours=24)
        ).count()
        if visits_24h >= 2: val += 10

        # Return visit within 7d
        if score.first_visit_at and score.first_visit_at < now - timedelta(days=7):
            if score.last_visit_at and score.last_visit_at >= now - timedelta(days=7):
                val += 10

        return min(100, val)

    @classmethod
    def _notify_score_change(cls, lead, score):
        from notifications.models import Notification
        emojis = {'cold': '❄️', 'warm': '🌡️', 'hot': '🔥', 'qualified': '✅'}
        emoji = emojis.get(score.score_tier, '')
        direction = '↑' if score.score_change > 0 else '↓'

        Notification.objects.create(
            user=lead.user,
            notification_type='lead_score_changed',
            title=f'{emoji} Lead Score {direction}: {lead.get_full_name()}',
            message=f'Score moved from {score.previous_score} to {score.total_score} ({score.score_tier.upper()})',
            related_object_type='lead',
            related_object_id=lead.id,
            action_url=f'/leads/{lead.id}',
        )

    @classmethod
    def batch_recalculate(cls, user_id=None):
        """Nightly batch recalculation."""
        from .models import LeadScore
        qs = LeadScore.objects.select_related('lead')
        if user_id:
            qs = qs.filter(user_id=user_id)
        count = 0
        for score in qs.iterator(chunk_size=100):
            try:
                cls.recalculate_score(str(score.lead.id))
                count += 1
            except Exception as e:
                logger.error(f"Score recalc failed for lead {score.lead.id}: {e}")
        logger.info(f"Batch recalculated {count} lead scores")
        return count
