from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer
from sales_app.models import Offer, OfferDetail, Order, Review


class StrictModelSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        """
        Make sure the input doesn't contain extra fields that shouldn't be there.
        """
        allowed = set(self.fields.keys())
        received = set(data.keys())
        unexpected = received - allowed
        if unexpected:
            raise serializers.ValidationError({
                "non_field_errors": f"Unexpected fields: {', '.join(unexpected)}"
            })
        return super().to_internal_value(data)


class OfferDetailUrlSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'url', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
        extra_kwargs = {
            'url': {'view_name': 'offer-detail-detail'},
            'offer': {'required': False},
        }


class OfferDetailSerializer(ModelSerializer):
    class Meta:
        model = OfferDetail
        exclude = ['offer']
        extra_kwargs = {
            'offer': {'required': False},
        }


class OfferBaseSerializer(ModelSerializer):
    user = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'image', 'description', 'details',
            'created_at', 'updated_at', 'user', 'user_details',
            'min_price', 'min_delivery_time'
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def get_min_price(self, obj):
        """
        Get the lowest price from all the offer
        """
        prices = obj.details.values_list('price', flat=True)
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        """
        Get the shortest delivery time from all the offer
        """
        times = obj.details.values_list('delivery_time_in_days', flat=True)
        return min(times) if times else None

    def get_user(self, obj):
        """
        Return the ID of the user who created the offer.
        """
        return obj.user_profile.id

    def get_user_details(self, obj):
        """
        Return the name and username of the user who created the offer.
        """
        user = obj.user_profile.user
        return {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
        }


class OfferReadSerializer(OfferBaseSerializer):
    details = OfferDetailUrlSerializer(many=True)


class OfferCreateSerializer(OfferBaseSerializer):
    details = OfferDetailSerializer(many=True)

    def create(self, validated_data):
        """
        Create a new offer with its packages (details).
        """
        request = self.context.get('request')
        user = request.user

        user_profile = getattr(user, 'userprofile', None)
        if not user_profile:
            raise serializers.ValidationError('User Profile does not exist.')

        details = validated_data.pop('details', [])
        offer = Offer.objects.create(user_profile=user_profile, **validated_data)

        for detail in details:
            serializer = OfferDetailSerializer(data=detail)
            serializer.is_valid(raise_exception=True)
            try:
                OfferDetail.objects.create(offer=offer, **serializer.validated_data)
            except IntegrityError:
                raise serializers.ValidationError({"detail": "Create Detail failed."})

        return offer

    def update(self, instance, validated_data):
        """
        Update the offer 
        """
        details_data = validated_data.pop('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            existing_details = {d.offer_type: d for d in instance.details.all()}
            for detail_data in details_data:
                offer_type = detail_data.get('offer_type')
                if offer_type in existing_details:
                    # Update existing package
                    detail = existing_details[offer_type]
                    for attr, value in detail_data.items():
                        setattr(detail, attr, value)
                    detail.save()
                else:
                    # Create new offer
                    try:
                         OfferDetail.objects.create(offer=instance, **detail_data)
                    except IntegrityError:
                        raise serializers.ValidationError({"detail": "Create Detail failed."})
                   

        return instance


class OrderSerializer(StrictModelSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True)

    revisions = serializers.SerializerMethodField()
    delivery_time_in_days = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    offer_type = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    business_user = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'title', 'customer_user', 'business_user', 'status', 'created_at', 'updated_at',
            'offer_detail_id', 'revisions', 'price', 'delivery_time_in_days', 'features', 'offer_type'
        ]
        extra_kwargs = {
            'customer_user': {'required': False},
        }

    

    def create(self, validated_data):
        """
        Create a new order based on the selected offer 
        """
        request = self.context.get('request')
        user = request.user

        customer_user = getattr(user, 'userprofile', None)
        if not customer_user:
            raise serializers.ValidationError('User Profile does not exist.')

        offer_detail_id = validated_data.pop('offer_detail_id')
        try:
            detail = OfferDetail.objects.get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            raise NotFound(detail="OfferDetail not found.")

        return Order.objects.create(customer_user=customer_user, offer_detail=detail)

    def get_revisions(self, obj):
        """
        Show how many revisions the order allows.
        """
        return obj.offer_detail.revisions

    def get_title(self, obj):
        """
        Show the title of the offer package.
        """
        return obj.offer_detail.title

    def get_price(self, obj):
        """
        Show the price of the offer package.
        """
        return obj.offer_detail.price

    def get_delivery_time_in_days(self, obj):
        """
        Show how long the order will take to deliver.
        """
        return obj.offer_detail.delivery_time_in_days

    def get_features(self, obj):
        """
        Show the features included in the order.
        """
        return obj.offer_detail.features

    def get_offer_type(self, obj):
        """
        Show the type of the offer package (basic, standard, premium).
        """
        return obj.offer_detail.offer_type

    def get_business_user(self, obj):
        """
        Return the ID of the business user providing the offer.
        """
        return obj.offer_detail.offer.user_profile.id


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        extra_kwargs = {
            'reviewer': {'required': False},
        }

    def create(self, validated_data):
        """
        Create a review. If the user already submitted one for the same business user, block it.
        """
        request = self.context.get('request')
        user = request.user

        try:
            return Review.objects.create(reviewer=user.userprofile, **validated_data)
        except IntegrityError:
            raise PermissionDenied("You have already submitted a review for this business user.")
