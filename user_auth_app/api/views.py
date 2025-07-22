import os

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer
from .permissions import IsOwnerOrReadOnly


def format_user_profile_response(user_profile):
    """
    Returns a dictionary of selected user and profile information 
    in a cleaner format for API responses.
    """
    user = user_profile.user

    if user_profile.file and user_profile.file.name:
        file = os.path.basename(user_profile.file.name)
    else: 
        file = None

    response_data = {
        "user": user_profile.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name":  user.last_name,
        "file": file,
        "location": user_profile.location,
        "tel": user_profile.tel,
        "description": user_profile.description,
        "working_hours": user_profile.working_hours,
        "type": user_profile.type,
        "email": user.email,
        "created_at": user_profile.created_at,
    }

    return response_data


class UserProfileListView(generics.ListAPIView):
    """
    Returns a list of all user profiles. Requires authentication.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        Returns a custom-formatted list of all user profiles.
        """
        business_users = self.get_queryset()
        query_set = [format_user_profile_response(user_profile) for user_profile in business_users]
        return Response(query_set, status=status.HTTP_200_OK)


class UserProfileBusinessListView(UserProfileListView):
    """
    Returns a list of all business user profiles.
    """
    def get_queryset(self):
        return UserProfile.objects.filter(type=UserProfile.BUSINESS)
        

class UserProfileCustomerListView(UserProfileListView):
    """
    Returns a list of all customer user profiles.
    """
    def get_queryset(self):
        return UserProfile.objects.filter(type=UserProfile.CUSTOMER)
    

class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Allows a user to view and update their own profile.
    Only the owner can update the profile.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        """
        Returns detailed profile information for one user.
        """
        response_data = format_user_profile_response(self.get_object())
        return Response(response_data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """
        Updates both user fields (like first name, email)
        and profile fields (like location, tel, etc.).
        """
        user_profile = self.get_object()
        user = user_profile.user
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        user.save()

        serializer = self.get_serializer(user_profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(format_user_profile_response(user_profile), status=status.HTTP_200_OK)


class UserProfileCreateView(generics.CreateAPIView):
    """
    Handles user registration and returns the created profile with an auth token.
    """
    queryset = UserProfile.objects.all()
    serializer_class = RegistrationSerializer

    def perform_create(self, serializer):
        """
        Saves the new user and profile.
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Registers a new user and profile, and returns an auth token.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        token, _ = Token.objects.get_or_create(user=profile.user)
        user = {
            "token": token.key,
            "username": profile.user.username,
            "email": profile.user.email,
            "user_id": profile.id
        }
        return Response(user, status=status.HTTP_201_CREATED)
    

class CustomLoginView(ObtainAuthToken):
    """
    Custom login view that returns token along with basic user info.
    """
    def post(self, request, *args, **kwargs):
        """
        Authenticates the user and returns their token, email, username, and user profile ID.
        """
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.userprofile.id
        }, status=status.HTTP_200_OK)
