

# Create your models here.
import uuid
from django.db import models

WIDGET_TYPE_CHOICES = [
    ('total_leads', 'Total Leads'), ('conversion_rate', 'Conversion Rate'),
    ('pipeline_value', 'Pipeline Value'), ('recent_activity', 'Recent Activity'),
    ('proposals_generated', 'Proposals Generated'), ('proposals_accepted', 'Proposals Accepted'),
    ('lead_score_distribution', 'Lead Score Distribution'),
    ('lead_source_breakdown', 'Lead Source Breakdown'),
    ('monthly_revenue', 'Monthly Revenue'), ('follow_up_reminders', 'Follow-up Reminders'),
    ('ai_usage_stats', 'AI Usage Stats'), ('top_performing_templates', 'Top Templates'),
]


def default_widget_position():
    return {"x": 0, "y": 0, "w": 6, "h": 4}


class DashboardWidget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='dashboard_widgets')
    widget_type = models.CharField(max_length=50, choices=WIDGET_TYPE_CHOICES, db_index=True)
    title = models.CharField(max_length=100)
    position = models.JSONField(default=default_widget_position)
    config = models.JSONField(default=dict)
    is_visible = models.BooleanField(default=True)
    refresh_interval_seconds = models.IntegerField(default=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dashboard_widgets'
        ordering = ['id']

    def __str__(self):
        return f"{self.user} — {self.widget_type}"