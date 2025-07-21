from django.contrib import admin
from django.urls import path

from .views import UserProfileCreateView, CustomLoginView, UserProfileDetailView, UserProfileBusinessListView, UserProfileCustomerListView

urlpatterns = [
    path('registration/', UserProfileCreateView.as_view(), name='registration'),
    path('login/', CustomLoginView.as_view(), name='registration'),
    path('profile/<int:pk>/', UserProfileDetailView.as_view(), name='user-profile-list'),
    path('profile/business/', UserProfileBusinessListView.as_view(), name='user-profile-business-list'),
    path('profile/customer/', UserProfileCustomerListView.as_view(), name='user-profile-customer-list'),
]
