import django_filters
from .models import Lead


class LeadFilter(django_filters.FilterSet):
    status = django_filters.MultipleChoiceFilter(choices=[
        ('new','New'),('contacted','Contacted'),('qualified','Qualified'),
        ('proposal_sent','Proposal Sent'),('negotiating','Negotiating'),
        ('closed_won','Closed Won'),('closed_lost','Closed Lost'),
        ('nurture','Nurture'),('disqualified','Disqualified'),
    ])
    priority = django_filters.MultipleChoiceFilter(choices=[
        ('low','Low'),('medium','Medium'),('high','High'),('urgent','Urgent'),
    ])
    source = django_filters.MultipleChoiceFilter(choices=[
        ('website_form','Website Form'),('upwork','Upwork'),('linkedin','LinkedIn'),
        ('referral','Referral'),('cold_outreach','Cold Outreach'),
        ('networking','Networking'),('other','Other'),
    ])
    is_hot = django_filters.BooleanFilter()
    company = django_filters.CharFilter(lookup_expr='icontains')
    industry = django_filters.CharFilter(lookup_expr='exact')
    company_size = django_filters.CharFilter(lookup_expr='exact')
    estimated_value_min = django_filters.NumberFilter(field_name='estimated_value', lookup_expr='gte')
    estimated_value_max = django_filters.NumberFilter(field_name='estimated_value', lookup_expr='lte')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    follow_up_before = django_filters.DateTimeFilter(field_name='next_follow_up_at', lookup_expr='lte')
    follow_up_overdue = django_filters.BooleanFilter(method='filter_overdue')
    score_tier = django_filters.CharFilter(field_name='score__score_tier')
    score_min = django_filters.NumberFilter(field_name='score__total_score', lookup_expr='gte')
    score_max = django_filters.NumberFilter(field_name='score__total_score', lookup_expr='lte')

    class Meta:
        model = Lead
        fields = ['status', 'priority', 'source', 'is_hot', 'industry', 'company_size']

    def filter_overdue(self, queryset, name, value):
        from django.utils import timezone
        if value:
            return queryset.filter(next_follow_up_at__lt=timezone.now(), next_follow_up_at__isnull=False)
        return queryset
