import uuid
from django.db import models
from django.conf import settings


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('lead_score_changed', 'Lead Score Changed'),
        ('proposal_accepted', 'Proposal Accepted'),
        ('follow_up_due', 'Follow-up Due'),
        ('quota_warning', 'Quota Warning'),
        ('new_lead', 'New Lead'),
        ('system', 'System'),
        ('ai_generation_complete', 'AI Generation Complete'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        db_index=True
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.UUIDField(null=True, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at'], name='notif_user_read_created_idx'),
        ]

    def __str__(self):
        return f"{self.notification_type}: {self.title}"
