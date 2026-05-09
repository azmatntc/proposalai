import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator


TIMEZONE_CHOICES = [
    ('UTC', 'UTC'), ('US/Eastern', 'Eastern'), ('US/Central', 'Central'),
    ('US/Mountain', 'Mountain'), ('US/Pacific', 'Pacific'),
    ('Europe/London', 'London'), ('Europe/Paris', 'Paris'),
    ('Asia/Tokyo', 'Tokyo'), ('Asia/Shanghai', 'Shanghai'),
    ('Asia/Kolkata', 'India'), ('Australia/Sydney', 'Sydney'),
]

SUBSCRIPTION_TIER_CHOICES = [('free', 'Free'), ('pro', 'Pro'), ('enterprise', 'Enterprise')]
MONTHLY_QUOTAS = {'free': 10, 'pro': 100, 'enterprise': 1000}


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True, validators=[EmailValidator()])
    username = models.CharField(max_length=150, unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    timezone = models.CharField(max_length=50, default='UTC', choices=TIMEZONE_CHOICES)
    subscription_tier = models.CharField(max_length=20, default='free', choices=SUBSCRIPTION_TIER_CHOICES, db_index=True)
    monthly_proposal_quota = models.IntegerField(default=10)
    proposals_generated_this_month = models.IntegerField(default=0)
    stripe_customer_id = models.CharField(max_length=255, blank=True, db_index=True)
    is_onboarded = models.BooleanField(default=False)
    onboarding_step = models.IntegerField(default=0)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email'], name='user_email_idx'),
            models.Index(fields=['subscription_tier', 'is_active'], name='user_tier_active_idx'),
        ]

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"

    def get_full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.email

    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]

    def has_reached_quota(self):
        return self.proposals_generated_this_month >= self.monthly_proposal_quota

    def get_remaining_quota(self):
        return max(0, self.monthly_proposal_quota - self.proposals_generated_this_month)

    def increment_proposal_count(self):
        User.objects.filter(pk=self.pk).update(
            proposals_generated_this_month=models.F('proposals_generated_this_month') + 1
        )
        self.refresh_from_db(fields=['proposals_generated_this_month'])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.monthly_proposal_quota = MONTHLY_QUOTAS.get(self.subscription_tier, 10)
        super().save(*args, **kwargs)