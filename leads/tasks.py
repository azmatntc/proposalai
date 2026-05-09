import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, name='leads.tasks.recalculate_lead_score')
def recalculate_lead_score(self, lead_id: str):
    from .scoring import LeadScoringService
    try:
        score = LeadScoringService.recalculate_score(lead_id)
        return {'lead_id': lead_id, 'score': score.total_score if score else None}
    except Exception as exc:
        logger.error(f"Score recalc failed for {lead_id}: {exc}")
        raise self.retry(exc=exc, countdown=30)


@shared_task(name='leads.tasks.batch_recalculate_scores')
def batch_recalculate_scores(user_id=None):
    from .scoring import LeadScoringService
    count = LeadScoringService.batch_recalculate(user_id)
    return {'recalculated': count}
