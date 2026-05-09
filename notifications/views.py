from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Notification
from .serializers import NotificationSerializer
from config.pagination import StandardResultsSetPagination


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() == 'true')
        return qs

    @action(detail=True, methods=['patch'])
    def read(self, request, pk=None):
        notif = self.get_object()
        notif.mark_read()
        return Response(NotificationSerializer(notif).data)

    @action(detail=False, methods=['post'], url_path='read-all')
    def read_all(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        return Response({'marked_read': count})

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})
