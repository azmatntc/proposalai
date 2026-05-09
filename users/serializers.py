from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm', 'company_name']

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username', validated_data['email'].split('@')[0]),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            company_name=validated_data.get('company_name', ''),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    short_name = serializers.CharField(source='get_short_name', read_only=True)
    remaining_quota = serializers.IntegerField(source='get_remaining_quota', read_only=True)
    has_reached_quota = serializers.BooleanField(read_only=True)
    avatar_url = serializers.SerializerMethodField()
    is_pro = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name', 'short_name',
            'avatar', 'avatar_url', 'bio', 'company_name', 'website', 'timezone',
            'subscription_tier', 'monthly_proposal_quota', 'proposals_generated_this_month',
            'remaining_quota', 'has_reached_quota', 'is_onboarded', 'onboarding_step',
            'email_verified', 'two_factor_enabled', 'preferences', 'is_pro',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'email', 'subscription_tier', 'monthly_proposal_quota',
                           'proposals_generated_this_month', 'created_at', 'updated_at']

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        name = obj.get_full_name().replace(' ', '+')
        return f"https://ui-avatars.com/api/?name={name}&background=3b82f6&color=fff&size=128"

    def get_is_pro(self, obj):
        return obj.subscription_tier in ['pro', 'enterprise']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'company_name', 'website', 'timezone', 'preferences']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match."})
        try:
            validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    uid = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match."})
        return data
