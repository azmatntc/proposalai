from rest_framework import serializers
from .models import AIUsageLog


class AIUsageLogSerializer(serializers.ModelSerializer):
    cost_display = serializers.SerializerMethodField()

    class Meta:
        model = AIUsageLog
        fields = [
            'id', 'proposal', 'model', 'prompt_tokens', 'completion_tokens',
            'total_tokens', 'cost_usd', 'cost_display', 'latency_ms',
            'was_cached', 'created_at',
        ]
        read_only_fields = fields

    def get_cost_display(self, obj):
        return f"${float(obj.cost_usd):.4f}"