import django_filters
from django_filters.rest_framework import FilterSet
from sales_app.models import Offer

class OfferFilter(FilterSet):
    """
    FilterSet for filtering Offer objects based on custom fields:
    - creator_id: Filters by the user_profile_id of the offer creator
    - max_delivery_time: Filters offers whose minimum delivery time across all packages is less than or equal to this value
    - min_price: Filters offers whose minimum price across all packages is greater than or equal to this value

    """

    creator_id = django_filters.NumberFilter(field_name='user_profile_id')
    max_delivery_time = django_filters.NumberFilter(field_name='min_delivery_time', lookup_expr='lte')
    min_price = django_filters.NumberFilter(field_name='min_price', lookup_expr='gte')

    class Meta:
        model = Offer
        fields = []  
