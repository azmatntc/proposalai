from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.utils import timezone

from .models import User
from .serializers import (
    RegisterSerializer, UserSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Issue tokens immediately on registration
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user, context={'request': request}).data

        return Response({
            'user': user_data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'message': 'Account created successfully.',
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower()
        password = request.data.get('password', '')

        if not email or not password:
            return Response(
                {'error': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=email, password=password)
        if not user:
            return Response(
                {'error': 'Invalid credentials. Please check your email and password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'Account is disabled.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update last login IP
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        if ip:
            user.last_login_ip = ip.split(',')[0].strip()
            user.save(update_fields=['last_login_ip'])

        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user, context={'request': request}).data

        return Response({
            'user': user_data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except TokenError:
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user, context={'request': request}).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': 'Password changed successfully.'})


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].lower()

        # Always return success to prevent email enumeration
        user = User.objects.filter(email=email).first()
        if user:
            # TODO: Generate token and send email
            pass

        return Response({'message': 'If that email exists, a reset link has been sent.'})


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if 'avatar' not in request.FILES:
            return Response({'error': 'No avatar file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        avatar_file = request.FILES['avatar']
        if avatar_file.size > 5 * 1024 * 1024:  # 5MB limit
            return Response({'error': 'Avatar must be under 5MB.'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.avatar:
            request.user.avatar.delete(save=False)

        request.user.avatar = avatar_file
        request.user.save(update_fields=['avatar'])

        return Response({'avatar_url': UserSerializer(request.user, context={'request': request}).data['avatar_url']})
