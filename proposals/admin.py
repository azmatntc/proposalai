from django.contrib import admin

from .models import Proposal, ProposalTemplate

@admin.register(ProposalTemplate)
class ProposalTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'category', 'tone', 'usage_count', 'is_system_template', 'is_active']
    list_filter = ['category', 'tone', 'is_system_template', 'is_public', 'is_active']
    search_fields = ['name', 'description', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'usage_count']

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'client_name', 'status', 'job_platform', 'word_count', 'ai_cost_usd', 'created_at']
    list_filter = ['status', 'job_platform', 'folder', 'is_active', 'tone_used']
    search_fields = ['title', 'client_name', 'client_email', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'ai_tokens_used', 'ai_cost_usd', 'generation_time_ms']
