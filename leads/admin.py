from django.contrib import admin
from .models import Lead, LeadActivity, LeadScore, LeadProposal

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'company', 'status', 'priority', 'user']
    list_filter = ['status', 'priority', 'source']
    search_fields = ['first_name', 'last_name', 'email', 'company']

@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):
    list_display = ['lead', 'activity_type', 'description', 'created_at']
    list_filter = ['activity_type', 'created_at']

@admin.register(LeadScore)
class LeadScoreAdmin(admin.ModelAdmin):
    list_display = ['lead', 'id']

@admin.register(LeadProposal)
class LeadProposalAdmin(admin.ModelAdmin):
    list_display = ['lead', 'proposal', 'status', 'sent_at']
    list_filter = ['status']
