from django.urls import path
from . import views

urlpatterns = [
    path('ai-usage/',          views.AIUsageListView.as_view(),       name='ai-usage-list'),
    path('ai-usage/summary/',  views.AIUsageSummaryView.as_view(),    name='ai-usage-summary'),
    path('ai-usage/by-model/', views.AIUsageByModelView.as_view(),    name='ai-usage-by-model'),
    path('overview/',          views.AnalyticsOverviewView.as_view(), name='analytics-overview'),
]