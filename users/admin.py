from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'subscription_tier', 'proposals_generated_this_month', 'is_active', 'created_at']
    list_filter = ['subscription_tier', 'is_active', 'email_verified', 'is_onboarded']
    search_fields = ['email', 'first_name', 'last_name', 'company_name']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login_ip']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('avatar', 'bio', 'company_name', 'website', 'timezone')}),
        ('Subscription', {'fields': ('subscription_tier', 'monthly_proposal_quota', 'proposals_generated_this_month', 'stripe_customer_id')}),
        ('Status', {'fields': ('is_onboarded', 'onboarding_step', 'email_verified', 'two_factor_enabled', 'last_login_ip')}),
        ('Preferences', {'fields': ('preferences',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
