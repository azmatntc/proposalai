import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.core.validators import MinValueValidator, MaxValueValidator


CATEGORY_CHOICES = [
    ('web_dev', 'Web Development'), ('mobile_app', 'Mobile App'),
    ('design', 'Design'), ('marketing', 'Marketing'),
    ('writing', 'Writing'), ('consulting', 'Consulting'), ('other', 'Other'),
]
TONE_CHOICES = [
    ('professional', 'Professional'), ('casual', 'Casual'),
    ('friendly', 'Friendly'), ('formal', 'Formal'),
    ('persuasive', 'Persuasive'), ('technical', 'Technical'),
]
PROPOSAL_STATUS_CHOICES = [
    ('draft', 'Draft'), ('generated', 'Generated'), ('edited', 'Edited'),
    ('sent', 'Sent'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('archived', 'Archived'),
]
PLATFORM_CHOICES = [
    ('upwork', 'Upwork'), ('freelancer', 'Freelancer'), ('fiverr', 'Fiverr'),
    ('linkedin', 'LinkedIn'), ('direct', 'Direct'), ('other', 'Other'),
]
FOLDER_CHOICES = [
    ('inbox', 'Inbox'), ('templates', 'Templates'), ('sent', 'Sent'), ('archived', 'Archived'),
]


class ProposalTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='templates', db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    tone = models.CharField(max_length=20, choices=TONE_CHOICES, default='professional')
    structure = models.JSONField(default=dict)
    default_variables = models.JSONField(default=dict)
    is_favorite = models.BooleanField(default=False, db_index=True)
    usage_count = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    is_system_template = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    tags = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'proposal_templates'
        ordering = ['-is_favorite', '-usage_count', '-created_at']
        indexes = [
            models.Index(fields=['user', 'category', 'is_active'], name='template_user_cat_idx'),
            models.Index(fields=['is_system_template', 'is_public', 'is_active'], name='template_system_public_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                condition=models.Q(deleted_at__isnull=True),
                name='unique_template_name_per_user'
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"

    def increment_usage(self):
        ProposalTemplate.objects.filter(pk=self.pk).update(usage_count=models.F('usage_count') + 1)

    def add_rating(self, rating: float):
        total = self.average_rating * self.usage_count
        new_count = self.usage_count + 1
        self.average_rating = (total + rating) / new_count
        self.save(update_fields=['average_rating'])

    def clone_for_user(self, user):
        self.pk = None
        self.id = uuid.uuid4()
        self.user = user
        self.is_system_template = False
        self.usage_count = 0
        self.name = f"Copy of {self.name}"
        self.save()
        return self

    def get_structure_sections(self):
        return self.structure.get('sections', [])


class Proposal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='proposals', db_index=True)
    template = models.ForeignKey(ProposalTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='proposals')
    title = models.CharField(max_length=255, db_index=True)
    client_name = models.CharField(max_length=255)
    client_company = models.CharField(max_length=255, blank=True)
    client_email = models.EmailField(blank=True)
    job_description = models.TextField()
    job_url = models.URLField(blank=True)
    job_platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, blank=True)
    generated_content = models.JSONField(default=dict)
    final_content = models.TextField(blank=True)
    tone_used = models.CharField(max_length=20, choices=TONE_CHOICES, default='professional')
    word_count = models.IntegerField(default=0)
    ai_model_used = models.CharField(max_length=50, default='gpt-4o')
    ai_tokens_used = models.IntegerField(default=0)
    ai_cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    generation_time_ms = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=PROPOSAL_STATUS_CHOICES, default='draft', db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    custom_variables = models.JSONField(default=dict)
    attachments = models.JSONField(default=list)
    notes = models.TextField(blank=True)
    rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback = models.TextField(blank=True)
    is_favorite = models.BooleanField(default=False)
    folder = models.CharField(max_length=100, default='inbox', choices=FOLDER_CHOICES, db_index=True)
    tags = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    search_vector = SearchVectorField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'proposals'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', 'is_active'], name='proposal_user_status_idx'),
            models.Index(fields=['user', 'folder', 'is_active'], name='proposal_user_folder_idx'),
            models.Index(fields=['client_email', 'is_active'], name='proposal_client_email_idx'),
            models.Index(fields=['job_platform', 'is_active'], name='proposal_platform_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=1, rating__lte=5) | models.Q(rating__isnull=True),
                name='valid_rating_range'
            ),
        ]

    def __str__(self):
        return f"{self.title} → {self.client_name}"

    def get_word_count(self):
        if self.final_content:
            return len(self.final_content.split())
        sections = self.generated_content.get('sections', [])
        text = ' '.join(s.get('content', '') for s in sections)
        return len(text.split())

    def duplicate(self):
        new = Proposal(
            user=self.user,
            template=self.template,
            title=f"Copy of {self.title}",
            client_name=self.client_name,
            client_company=self.client_company,
            client_email=self.client_email,
            job_description=self.job_description,
            job_platform=self.job_platform,
            tone_used=self.tone_used,
            custom_variables=self.custom_variables,
            notes=self.notes,
            tags=self.tags[:],
            status='draft',
        )
        new.save()
        return new

    def get_status_display_color(self):
        colors = {
            'draft': 'gray', 'generated': 'blue', 'edited': 'indigo',
            'sent': 'amber', 'accepted': 'green', 'rejected': 'red', 'archived': 'gray',
        }
        return colors.get(self.status, 'gray')

    def soft_delete(self):
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['deleted_at', 'is_active'])
