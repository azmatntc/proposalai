from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProposalTemplateViewSet

router = DefaultRouter()
router.register(r'', ProposalTemplateViewSet, basename='template')
urlpatterns = [path('', include(router.urls))]
