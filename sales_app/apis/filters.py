import django_filters
from django_filters.rest_framework import FilterSet
from sales_app.models import Offer 

class OfferFilter(FilterSet):
    creator_id = django_filters.NumberFilter(field_name='user_profile_id')
    max_delivery_time = django_filters.NumberFilter(field_name='min_delivery_time', lookup_expr='lte')
    min_price = django_filters.NumberFilter(field_name='min_price', lookup_expr='gte')

    class Meta:
        model = Offer
        fields = []
