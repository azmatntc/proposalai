import uuid
from django.db import models


class AIUsageLog(models.Model):
    """Tracks every AI generation request for cost monitoring."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='ai_usage_logs'
    )
    proposal = models.ForeignKey(
        'proposals.Proposal', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='ai_usage_logs'
    )
    model = models.CharField(max_length=50)
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    latency_ms = models.IntegerField(default=0)
    prompt_template_used = models.CharField(max_length=255, blank=True)
    was_cached = models.BooleanField(default=False)
    cache_hit = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_usage_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at'], name='ai_usage_user_created_idx'),
            models.Index(fields=['model', 'created_at'], name='ai_usage_model_created_idx'),
        ]

    def __str__(self):
        return f"{self.user.email} — {self.model} — {self.total_tokens} tokens"