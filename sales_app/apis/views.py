from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework import status
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min, Max, Avg


from sales_app.models import Offer, OfferDetail, Order, UserProfile, Review
from .serializers import OfferCreateSerializer, OfferReadSerializer, OfferDetailSerializer, OrderSerializer, ReviewSerializer
from .permissions import IsBusinessUser, IsBusinessOwerOrReadOnly, IsCustomerUser, IsStaffForDeleteOrBusinessForPatch, IsUserWithProfile, IsReviewerSelf
from .filters import OfferFilter

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100


class OfferListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsBusinessUser]
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['updated_at']

    def get_serializer_class(self):
        """
        Use the read serializer for GET requests and the write serializer for POST requests.
        """
        if self.request.method == 'GET':
            return OfferReadSerializer 
        else:
            return OfferCreateSerializer

    def get_queryset(self):
        """
        Get all offers with extra fields for minimum price and delivery time.
        """
        return Offer.objects.annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days')
        )
    
    def post(self, request, *args, **kwargs):
        """
        Create a new offer. Removes the 'url' field from details in the response.
        """
        response =  super().post(request, *args, **kwargs)

        if 'details' in response.data:
            for detail in response.data['details']:
                detail.pop('url', None)

        return response
    
    def list(self, request, *args, **kwargs):
        """
        Get a list of offers. For each offer, show only id and URL of details.
        """
        response = super().list(request, *args, **kwargs)

        for offer in response.data['results']: 
            offer['details'] = [
                {
                    'id': d['id'],
                    'url': d['url']
                }
                for d in offer['details']
            ]

        return response
        

class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    permission_classes = [IsBusinessOwerOrReadOnly]

    def get_serializer_class(self):
        """
        Use the write serializer for changes, and read serializer for viewing.
        """
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return OfferCreateSerializer 
        else:
            return OfferReadSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Get a single offer with simplified detail info (id + URL only).
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        if 'details' in data:
            data['details'] = [
                {
                    'id': d['id'],
                    'url': d['url']
                }
                for d in data['details']
            ]

        return Response(data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """
        Update an offer and remove the 'url' field from details in the response.
        """
        response = super().update(request, *args, **kwargs)

        if 'details' in response.data:
            for detail in response.data['details']:
                detail.pop('url', None)

        return response


class OfferDetailDetailView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsCustomerUser]
    serializer_class = OrderSerializer


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsStaffForDeleteOrBusinessForPatch]
    serializer_class = OrderSerializer


class OrderCountForBusinessView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """
        Return the number of in-progress orders for a business user.
        """
        try:
            business_user = UserProfile.objects.get(id=business_user_id, type='business')
        except UserProfile.DoesNotExist:
            raise NotFound({'detail': 'This id does not exist'})

        count = Order.objects.filter(
            offer_detail__offer__user_profile__id=business_user_id,
            status=Order.Status.IN_PROGRESS
        ).count()

        return Response({
            "order_count": count
        }, status=status.HTTP_200_OK)
    

class CompletedOrderCountForBusinessView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """
        Return the number of completed orders for a business user.
        """
        try:
            UserProfile.objects.get(id=business_user_id, type='business')
        except UserProfile.DoesNotExist:
            raise NotFound({'detail': 'This id does not exist'})

        count = Order.objects.filter(
            offer_detail__offer__user_profile__id=business_user_id,
            status=Order.Status.COMPLETED
        ).count()

        return Response({
            "order_count": count
        }, status=status.HTTP_200_OK)
    

class ReviewListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsUserWithProfile]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['updated_at', 'rating']
    filterset_fields = ['business_user_id', 'reviewer_id']
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsReviewerSelf]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Return total reviews, average rating, number of business profiles, and total offers.
        """
        average = Review.objects.aggregate(avg_rating=Avg('rating'))['avg_rating']
        average_rating = round(average, 1) if average else 0.0

        return Response({
            "review_count": Review.objects.all().count(),
            "average_rating": average_rating,
            "business_profile_count": UserProfile.objects.filter(type='business').count(),
            "offer_count": Offer.objects.all().count()
        }, status=status.HTTP_200_OK)
