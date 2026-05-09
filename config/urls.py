from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

api_v1_patterns = [
    path('auth/',        include('users.urls')),
    path('proposals/',   include('proposals.urls')),
    path('templates/',   include('proposals.template_urls')),
    path('leads/',       include('leads.urls')),
    path('dashboard/',   include('dashboard.urls')),
    path('analytics/',   include('analytics.urls')),       # ← NEW
    path('notifications/', include('notifications.urls')),
    path('schema/',      SpectacularAPIView.as_view(),                    name='schema'),
    path('docs/',        SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/',       SpectacularRedocView.as_view(url_name='schema'),  name='redoc'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_patterns)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)