from django.contrib import admin
from django.urls import path

from .views import UserProfileCreateView, CustomLoginView, UserProfileDetailView, UserProfileBusinessListView, UserProfileCustomerListView

# urls
urlpatterns = [
    path('registration/', UserProfileCreateView.as_view(), name='registration'),
    path('login/', CustomLoginView.as_view(), name='registration'),
    path('profile/<int:pk>/', UserProfileDetailView.as_view(), name='user-profile-list'),
    path('profiles/business/', UserProfileBusinessListView.as_view(), name='user-profile-business-list'),
    path('profiles/customer/', UserProfileCustomerListView.as_view(), name='user-profile-customer-list'),
]
