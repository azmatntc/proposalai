import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender='leads.Lead')
def lead_created_handler(sender, instance, created, **kwargs):
    if not created:
        return
    from .models import LeadScore, LeadActivity
    from notifications.models import Notification

    LeadScore.objects.get_or_create(lead=instance, defaults={'user': instance.user})

    LeadActivity.objects.create(
        lead=instance, user=instance.user,
        activity_type='imported' if instance.source == 'other' else 'note_added',
        description=f'Lead added from {instance.get_source_display()}',
        is_system_generated=True,
    )

    Notification.objects.create(
        user=instance.user,
        notification_type='new_lead',
        title=f'🎯 New Lead: {instance.get_full_name()}',
        message=f'From {instance.get_source_display()}',
        related_object_type='lead',
        related_object_id=instance.id,
        action_url=f'/leads/{instance.id}',
    )


@receiver(post_save, sender='leads.LeadActivity')
def activity_logged_handler(sender, instance, created, **kwargs):
    if not created or instance.is_system_generated:
        return
    from django.utils import timezone
    # Update last contact
    instance.lead.last_contact_at = instance.created_at
    instance.lead.save(update_fields=['last_contact_at'])
    # Async score recalculation
    try:
        from .tasks import recalculate_lead_score
        recalculate_lead_score.delay(str(instance.lead.id))
    except Exception as e:
        logger.warning(f"Could not queue score recalc: {e}")
