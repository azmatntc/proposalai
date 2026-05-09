from django.contrib import admin
from .models import AIUsageLog


@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
    list_display    = ['user', 'model', 'total_tokens', 'cost_usd', 'latency_ms', 'was_cached', 'created_at']
    list_filter     = ['model', 'was_cached', 'cache_hit']
    search_fields   = ['user__email', 'prompt_template_used']
    readonly_fields = ['id', 'created_at']
    ordering        = ['-created_at']
    date_hierarchy  = 'created_at'