import django_filters
from .models import Proposal, ProposalTemplate


class ProposalFilter(django_filters.FilterSet):
    status        = django_filters.MultipleChoiceFilter(choices=[
        ('draft','Draft'),('generated','Generated'),('edited','Edited'),
        ('sent','Sent'),('accepted','Accepted'),('rejected','Rejected'),('archived','Archived'),
    ])
    folder        = django_filters.CharFilter(lookup_expr='exact')
    job_platform  = django_filters.MultipleChoiceFilter(choices=[
        ('upwork','Upwork'),('freelancer','Freelancer'),('fiverr','Fiverr'),
        ('linkedin','LinkedIn'),('direct','Direct'),('other','Other'),
    ])
    is_favorite   = django_filters.BooleanFilter()
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before= django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    client_name   = django_filters.CharFilter(lookup_expr='icontains')
    client_company= django_filters.CharFilter(lookup_expr='icontains')
    rating_gte    = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')

    class Meta:
        model  = Proposal
        fields = ['status', 'folder', 'job_platform', 'is_favorite']


class ProposalTemplateFilter(django_filters.FilterSet):
    category          = django_filters.MultipleChoiceFilter(choices=[
        ('web_dev','Web Development'),('mobile_app','Mobile App'),('design','Design'),
        ('marketing','Marketing'),('writing','Writing'),('consulting','Consulting'),('other','Other'),
    ])
    tone              = django_filters.CharFilter(lookup_expr='exact')
    is_favorite       = django_filters.BooleanFilter()
    is_system_template= django_filters.BooleanFilter()
    is_public         = django_filters.BooleanFilter()
    name              = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model  = ProposalTemplate
        fields = ['category', 'tone', 'is_favorite', 'is_system_template', 'is_public']