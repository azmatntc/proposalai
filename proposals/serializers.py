
import bleach
from rest_framework import serializers
from django.core.validators import validate_email
from .models import Proposal, ProposalTemplate



class ProposalTemplateSerializer(serializers.ModelSerializer):
    section_count = serializers.SerializerMethodField()
    usage_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProposalTemplate
        fields = '__all__'
        read_only_fields = ['id', 'user', 'usage_count', 'average_rating', 'created_at', 'updated_at']

    def get_section_count(self, obj):
        return len(obj.get_structure_sections())

    def validate_structure(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Structure must be a JSON object.")
        sections = value.get('sections', [])
        if not isinstance(sections, list):
            raise serializers.ValidationError("Structure must contain a 'sections' array.")
        for i, section in enumerate(sections):
            if not section.get('name'):
                raise serializers.ValidationError(f"Section {i+1} must have a 'name'.")
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProposalListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    template_name = serializers.CharField(source='template.name', read_only=True, default=None)
    status_color = serializers.CharField(source='get_status_display_color', read_only=True)

    class Meta:
        model = Proposal
        fields = [
            'id', 'title', 'client_name', 'client_company', 'client_email',
            'job_platform', 'status', 'status_color', 'template_name',
            'tone_used', 'word_count', 'is_favorite', 'folder', 'tags',
            'sent_at', 'accepted_at', 'rating', 'created_at', 'updated_at',
        ]


class ProposalSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True, default=None)
    status_color = serializers.CharField(source='get_status_display_color', read_only=True)
    ai_cost_display = serializers.SerializerMethodField()
    linked_leads_count = serializers.IntegerField(source='leads.count', read_only=True)

    class Meta:
        model = Proposal
        fields = '__all__'
        read_only_fields = [
            'id', 'user', 'ai_tokens_used', 'ai_cost_usd',
            'generation_time_ms', 'ai_model_used', 'search_vector',
            'created_at', 'updated_at',
        ]

    def get_ai_cost_display(self, obj):
        if obj.ai_cost_usd:
            return f"${float(obj.ai_cost_usd):.4f}"
        return "$0.0000"

    def validate_job_description(self, value):
        cleaned = bleach.clean(
            value,
            tags=['p', 'br', 'strong', 'em', 'ul', 'ol', 'li'],
            strip=True
        )
        if len(cleaned.strip()) < 20:
            raise serializers.ValidationError("Job description must be at least 20 characters.")
        if len(cleaned) > 10000:
            raise serializers.ValidationError("Job description must be under 10,000 characters.")
        return cleaned

    def validate_client_email(self, value):
        if value:
            try:
                validate_email(value)
            except Exception:
                raise serializers.ValidationError("Enter a valid email address.")
        return value

    def validate_custom_variables(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Custom variables must be a JSON object.")
        if len(str(value)) > 10000:
            raise serializers.ValidationError("Custom variables too large.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request and request.method == 'POST':
            if request.user.has_reached_quota():
                raise serializers.ValidationError({
                    'quota': 'Monthly proposal quota exceeded. Please upgrade to Pro.',
                    'upgrade_url': '/upgrade'
                })
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # Set word count
        proposal = super().create(validated_data)
        proposal.word_count = proposal.get_word_count()
        proposal.save(update_fields=['word_count'])
        return proposal

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.word_count = instance.get_word_count()
        instance.save(update_fields=['word_count'])
        return instance
