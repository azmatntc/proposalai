from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('activity/', views.DashboardActivityView.as_view(), name='dashboard-activity'),
    path('pipeline/', views.DashboardPipelineView.as_view(), name='dashboard-pipeline'),
    path('revenue/', views.DashboardRevenueView.as_view(), name='dashboard-revenue'),
    path('ai-usage/', views.DashboardAIUsageView.as_view(), name='dashboard-ai-usage'),
]
