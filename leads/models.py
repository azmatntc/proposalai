import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.core.validators import MinValueValidator, MaxValueValidator


LEAD_STATUS_CHOICES = [
    ('new', 'New'), ('contacted', 'Contacted'), ('qualified', 'Qualified'),
    ('proposal_sent', 'Proposal Sent'), ('negotiating', 'Negotiating'),
    ('closed_won', 'Closed Won'), ('closed_lost', 'Closed Lost'),
    ('nurture', 'Nurture'), ('disqualified', 'Disqualified'),
]
PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')]
SOURCE_CHOICES = [
    ('website_form', 'Website Form'), ('upwork', 'Upwork'), ('linkedin', 'LinkedIn'),
    ('referral', 'Referral'), ('cold_outreach', 'Cold Outreach'),
    ('networking', 'Networking'), ('other', 'Other'),
]
INDUSTRY_CHOICES = [
    ('technology', 'Technology'), ('healthcare', 'Healthcare'), ('finance', 'Finance'),
    ('education', 'Education'), ('retail', 'Retail'), ('real_estate', 'Real Estate'),
    ('manufacturing', 'Manufacturing'), ('media', 'Media'), ('consulting', 'Consulting'), ('other', 'Other'),
]
COMPANY_SIZE_CHOICES = [
    ('1-10', '1-10'), ('11-50', '11-50'), ('51-200', '51-200'),
    ('201-500', '201-500'), ('501-1000', '501-1000'), ('1000+', '1000+'),
]
ACTIVITY_TYPE_CHOICES = [
    ('note_added', 'Note Added'), ('email_sent', 'Email Sent'), ('call_made', 'Call Made'),
    ('meeting_scheduled', 'Meeting Scheduled'), ('proposal_sent', 'Proposal Sent'),
    ('proposal_viewed', 'Proposal Viewed'), ('status_changed', 'Status Changed'),
    ('follow_up_set', 'Follow-up Set'), ('task_completed', 'Task Completed'),
    ('imported', 'Imported'), ('ai_generated', 'AI Generated'),
    ('email_opened', 'Email Opened'), ('link_clicked', 'Link Clicked'),
    ('website_visit', 'Website Visit'), ('form_submitted', 'Form Submitted'),
]
SCORE_TIER_CHOICES = [('cold', 'Cold'), ('warm', 'Warm'), ('hot', 'Hot'), ('qualified', 'Qualified')]


def default_scoring_weights():
    return {
        "engagement": 0.25,
        "recency": 0.20,
        "frequency": 0.20,
        "depth": 0.15,
        "demographic": 0.10,
        "intent": 0.10
    }


class Lead(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='leads', db_index=True)
    proposals = models.ManyToManyField('proposals.Proposal', through='LeadProposal', blank=True, related_name='leads')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=255, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, db_index=True)
    source_detail = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default='new', db_index=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', db_index=True)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    probability = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    expected_close_date = models.DateField(null=True, blank=True)
    actual_close_date = models.DateField(null=True, blank=True)
    close_reason = models.TextField(blank=True)
    industry = models.CharField(max_length=100, blank=True, choices=INDUSTRY_CHOICES)
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES, blank=True)
    location = models.CharField(max_length=255, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    tags = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    last_contact_at = models.DateTimeField(null=True, blank=True, db_index=True)
    next_follow_up_at = models.DateTimeField(null=True, blank=True, db_index=True)
    assigned_to = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads'
    )
    is_hot = models.BooleanField(default=False, db_index=True)
    search_vector = SearchVectorField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leads'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', 'priority', 'is_active'], name='lead_user_status_priority_idx'),
            models.Index(fields=['user', 'source', 'is_active'], name='lead_user_source_idx'),
            models.Index(fields=['email', 'is_active'], name='lead_email_idx'),
            models.Index(fields=['estimated_value', 'is_active'], name='lead_value_idx'),
            models.Index(fields=['expected_close_date', 'is_active'], name='lead_close_date_idx'),
            models.Index(fields=['next_follow_up_at', 'is_active'], name='lead_follow_up_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'email'],
                condition=models.Q(deleted_at__isnull=True),
                name='unique_lead_email_per_user'
            ),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.company})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_initials(self):
        parts = [self.first_name[:1], self.last_name[:1]]
        return ''.join(parts).upper() or self.email[:2].upper()

    def get_status_color(self):
        colors = {
            'new': 'indigo', 'contacted': 'blue', 'qualified': 'violet',
            'proposal_sent': 'amber', 'negotiating': 'orange',
            'closed_won': 'green', 'closed_lost': 'red',
            'nurture': 'cyan', 'disqualified': 'gray',
        }
        return colors.get(self.status, 'gray')

    def get_priority_color(self):
        return {'low': 'gray', 'medium': 'blue', 'high': 'orange', 'urgent': 'red'}.get(self.priority, 'gray')

    def days_since_last_contact(self):
        if not self.last_contact_at:
            return None
        from django.utils import timezone
        return (timezone.now() - self.last_contact_at).days

    def days_until_follow_up(self):
        if not self.next_follow_up_at:
            return None
        from django.utils import timezone
        delta = self.next_follow_up_at - timezone.now()
        return delta.days

    def update_last_contact(self):
        from django.utils import timezone
        self.last_contact_at = timezone.now()
        self.save(update_fields=['last_contact_at'])

    def soft_delete(self):
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['deleted_at', 'is_active'])


class LeadActivity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities', db_index=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='lead_activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPE_CHOICES, db_index=True)
    description = models.TextField()
    metadata = models.JSONField(default=dict)
    performed_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='performed_activities'
    )
    is_system_generated = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'lead_activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['lead', 'activity_type', 'created_at'], name='activity_lead_type_created_idx'),
            models.Index(fields=['user', 'created_at'], name='activity_user_created_idx'),
        ]

    def __str__(self):
        return f"{self.activity_type} — {self.lead}"

    def get_activity_icon(self):
        icons = {
            'note_added': 'StickyNote', 'email_sent': 'Mail', 'call_made': 'Phone',
            'meeting_scheduled': 'Calendar', 'proposal_sent': 'Send',
            'proposal_viewed': 'Eye', 'status_changed': 'RefreshCw',
            'follow_up_set': 'Clock', 'task_completed': 'CheckCircle',
            'imported': 'Download', 'ai_generated': 'Sparkles',
            'email_opened': 'MailOpen', 'link_clicked': 'ExternalLink',
            'website_visit': 'Globe', 'form_submitted': 'FileText',
        }
        return icons.get(self.activity_type, 'Circle')

    def get_activity_color(self):
        colors = {
            'email_sent': 'blue', 'call_made': 'green', 'meeting_scheduled': 'purple',
            'proposal_sent': 'amber', 'proposal_viewed': 'indigo',
            'status_changed': 'orange', 'task_completed': 'green',
            'ai_generated': 'violet', 'note_added': 'gray',
        }
        return colors.get(self.activity_type, 'gray')


class LeadScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name='score', db_index=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='lead_scores')

    # Raw engagement data
    total_website_visits = models.IntegerField(default=0)
    total_pages_viewed = models.IntegerField(default=0)
    total_time_on_site_seconds = models.IntegerField(default=0)
    email_opens_count = models.IntegerField(default=0)
    email_clicks_count = models.IntegerField(default=0)
    proposal_views_count = models.IntegerField(default=0)
    proposal_time_spent_seconds = models.IntegerField(default=0)
    form_submissions_count = models.IntegerField(default=0)
    calls_scheduled_count = models.IntegerField(default=0)
    meetings_attended_count = models.IntegerField(default=0)
    social_interactions_count = models.IntegerField(default=0)
    content_downloads_count = models.IntegerField(default=0)

    # Recency tracking
    first_visit_at = models.DateTimeField(null=True, blank=True)
    last_visit_at = models.DateTimeField(null=True, blank=True)
    last_email_open_at = models.DateTimeField(null=True, blank=True)
    last_proposal_view_at = models.DateTimeField(null=True, blank=True)

    # Sub-scores (0-100 each)
    engagement_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    recency_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    frequency_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    depth_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    demographic_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    intent_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    # Composite
    total_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    score_tier = models.CharField(max_length=20, choices=SCORE_TIER_CHOICES, default='cold', db_index=True)
    previous_score = models.IntegerField(default=0)
    score_change = models.IntegerField(default=0)
    score_history = models.JSONField(default=list)

    # Scoring Configuration
    scoring_weights = models.JSONField(default=default_scoring_weights)

    last_calculated_at = models.DateTimeField(auto_now=True)
    next_calculation_due = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lead_scores'
        indexes = [
            models.Index(fields=['user', 'total_score'], name='score_user_total_idx'),
            models.Index(fields=['score_tier', 'total_score'], name='score_tier_total_idx'),
        ]

    def __str__(self):
        return f"{self.lead} — {self.total_score} ({self.score_tier})"

    def calculate_total_score(self):
        w = self.scoring_weights
        self.total_score = round(
            self.engagement_score * w['engagement'] +
            self.recency_score * w['recency'] +
            self.frequency_score * w['frequency'] +
            self.depth_score * w['depth'] +
            self.demographic_score * w['demographic'] +
            self.intent_score * w['intent']
        )
        self.total_score = max(0, min(100, self.total_score))

    def update_score_tier(self):
        if self.total_score <= 25:
            self.score_tier = 'cold'
        elif self.total_score <= 50:
            self.score_tier = 'warm'
        elif self.total_score <= 75:
            self.score_tier = 'hot'
        else:
            self.score_tier = 'qualified'

    def record_history(self):
        from django.utils import timezone
        entry = {'date': timezone.now().date().isoformat(), 'score': self.total_score}
        history = self.score_history if isinstance(self.score_history, list) else []
        history.append(entry)
        self.score_history = history[-90:]  # Keep last 90 entries

    def get_score_breakdown(self):
        w = self.scoring_weights
        return {
            'engagement': {'score': self.engagement_score, 'weight': w['engagement'], 'weighted': round(self.engagement_score * w['engagement'])},
            'recency': {'score': self.recency_score, 'weight': w['recency'], 'weighted': round(self.recency_score * w['recency'])},
            'frequency': {'score': self.frequency_score, 'weight': w['frequency'], 'weighted': round(self.frequency_score * w['frequency'])},
            'depth': {'score': self.depth_score, 'weight': w['depth'], 'weighted': round(self.depth_score * w['depth'])},
            'demographic': {'score': self.demographic_score, 'weight': w['demographic'], 'weighted': round(self.demographic_score * w['demographic'])},
            'intent': {'score': self.intent_score, 'weight': w['intent'], 'weighted': round(self.intent_score * w['intent'])},
        }


class LeadProposal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    proposal = models.ForeignKey('proposals.Proposal', on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('sent','Sent'),('opened','Opened'),('clicked','Clicked'),('replied','Replied'),('converted','Converted'),('bounced','Bounced')],
        default='sent'
    )
    tracking_id = models.UUIDField(default=uuid.uuid4, unique=True)

    class Meta:
        db_table = 'lead_proposals'
        unique_together = ['lead', 'proposal']