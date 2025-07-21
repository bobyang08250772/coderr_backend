from django.contrib import admin
from .models import Offer, OfferDetail, Order, Review

# Register your models here.
@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'username', 'created_at', 'updated_at']

    def username(self, obj):
        return obj.user_profile.user.username
    

@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'offer_name']

    def offer_name(self, obj):
        return obj.offer.title
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'offer_provider']
    readonly_fields = ['offer_provider'] 

    def offer_provider(self, obj):
        return obj.offer_detail.offer.user_profile
    

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id']

        

    

