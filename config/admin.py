cat > ~/projects/proposalai/users/admin.py << 'EOF'
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'subscription_tier', 'is_active']
    list_filter = ['subscription_tier', 'is_active', 'email_verified']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('avatar', 'bio', 'company_name', 'website', 'timezone')}),
        ('Subscription', {'fields': ('subscription_tier', 'monthly_proposal_quota', 'proposals_generated_this_month', 'stripe_customer_id')}),
        ('Onboarding', {'fields': ('is_onboarded', 'onboarding_step')}),
        ('Security', {'fields': ('email_verified', 'two_factor_enabled', 'last_login_ip')}),
        ('Preferences', {'fields': ('preferences',)}),
    )
EOF