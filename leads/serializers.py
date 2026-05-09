from rest_framework import serializers
from .models import Lead, LeadActivity, LeadScore, LeadProposal


class LeadActivitySerializer(serializers.ModelSerializer):
    activity_icon = serializers.CharField(source='get_activity_icon', read_only=True)
    activity_color = serializers.CharField(source='get_activity_color', read_only=True)
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LeadActivity
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at']

    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return obj.performed_by.get_full_name()
        return None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class LeadScoreSerializer(serializers.ModelSerializer):
    breakdown = serializers.SerializerMethodField()
    trend = serializers.SerializerMethodField()
    recommendations = serializers.SerializerMethodField()

    class Meta:
        model = LeadScore
        fields = '__all__'
        read_only_fields = ['id', 'lead', 'user', 'created_at', 'updated_at', 'last_calculated_at']

    def get_breakdown(self, obj):
        return obj.get_score_breakdown()

    def get_trend(self, obj):
        history = obj.score_history[-7:] if isinstance(obj.score_history, list) else []
        direction = 'up' if obj.score_change > 0 else ('down' if obj.score_change < 0 else 'stable')
        return {'direction': direction, 'change': obj.score_change, 'history': history}

    def get_recommendations(self, obj):
        recs = []
        if obj.engagement_score < 30:
            recs.append({'type': 'engagement', 'priority': 'high', 'message': 'Send a follow-up email or share relevant content.'})
        if obj.recency_score < 20:
            recs.append({'type': 'recency', 'priority': 'medium', 'message': 'Lead has gone cold. Re-engage with a personalized message.'})
        if obj.intent_score < 20:
            recs.append({'type': 'intent', 'priority': 'medium', 'message': 'Share a case study or pricing information to signal value.'})
        if obj.demographic_score < 50:
            recs.append({'type': 'demographic', 'priority': 'low', 'message': 'Gather more info: company size, industry, LinkedIn profile.'})
        return recs


class LeadListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    initials = serializers.CharField(source='get_initials', read_only=True)
    status_color = serializers.CharField(source='get_status_color', read_only=True)
    priority_color = serializers.CharField(source='get_priority_color', read_only=True)
    score_summary = serializers.SerializerMethodField()
    days_since_contact = serializers.IntegerField(source='days_since_last_contact', read_only=True)

    class Meta:
        model = Lead
        fields = [
            'id', 'full_name', 'initials', 'first_name', 'last_name',
            'email', 'phone', 'company', 'job_title', 'source', 'status',
            'status_color', 'priority', 'priority_color', 'estimated_value',
            'currency', 'is_hot', 'tags', 'score_summary', 'days_since_contact',
            'next_follow_up_at', 'last_contact_at', 'created_at',
        ]

    def get_score_summary(self, obj):
        if hasattr(obj, 'score'):
            return {
                'total': obj.score.total_score,
                'tier': obj.score.score_tier,
                'change': obj.score.score_change,
            }
        return None


class LeadSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    initials = serializers.CharField(source='get_initials', read_only=True)
    status_color = serializers.CharField(source='get_status_color', read_only=True)
    priority_color = serializers.CharField(source='get_priority_color', read_only=True)
    score = LeadScoreSerializer(read_only=True)
    recent_activities = serializers.SerializerMethodField()
    linked_proposals_count = serializers.IntegerField(source='proposals.count', read_only=True)
    days_since_contact = serializers.IntegerField(source='days_since_last_contact', read_only=True)
    days_until_follow_up = serializers.IntegerField(read_only=True)

    class Meta:
        model = Lead
        fields = '__all__'
        read_only_fields = ['id', 'user', 'search_vector', 'created_at', 'updated_at']

    def get_recent_activities(self, obj):
        activities = obj.activities.select_related('user').order_by('-created_at')[:5]
        return LeadActivitySerializer(activities, many=True, context=self.context).data

    def validate_email(self, value):
        if value:
            return value.lower()
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
