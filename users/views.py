from rest_framework import status, viewsets, mixins, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from users.serializers import UserRegistrationSerializer, UserSerializer
from users.permissions import IsOwnerOrReadOnly

from rest_framework.decorators import action
from .models import Follow

User = get_user_model()


class UserRegistrationView(CreateAPIView):
    """
    API view for user registration.
    Returns user data and an authentication token upon successful registration.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate token for the newly created user
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user data and token
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class UserLogoutView(APIView):
    """
    API view for user logout.
    Deletes the authentication token assigned to the user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Delete the token to force login on next request
            request.user.auth_token.delete()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    ViewSet for viewing, searching, and updating user profiles.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'bio']

    # --- НОВЫЙ КОД НИЖЕ ---

    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        """Endpoint to follow a user."""
        target_user = self.get_object() # Gets the user we want to follow

        if target_user == request.user:
            return Response(
                {"detail": "You cannot follow yourself."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # get_or_create prevents errors if the user clicks "follow" twice
        follow_obj, created = Follow.objects.get_or_create(
            follower=request.user, 
            following=target_user
        )
        
        if not created:
            return Response(
                {"detail": "You are already following this user."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response(
            {"detail": "Successfully followed."}, 
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        """Endpoint to unfollow a user."""
        target_user = self.get_object()
        
        # Try to find the follow relationship and delete it
        deleted_count, _ = Follow.objects.filter(
            follower=request.user, 
            following=target_user
        ).delete()
        
        if deleted_count:
            return Response(
                {"detail": "Successfully unfollowed."}, 
                status=status.HTTP_200_OK
            )
            
        return Response(
            {"detail": "You are not following this user."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        """Endpoint to get a list of users following the specified user."""
        user = self.get_object()
        
        # Get IDs of all followers
        follower_ids = Follow.objects.filter(following=user).values_list('follower_id', flat=True)
        # Fetch the User objects
        followers_qs = User.objects.filter(id__in=follower_ids)
        
        # Paginate and serialize using the existing UserSerializer
        page = self.paginate_queryset(followers_qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(followers_qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        """Endpoint to get a list of users the specified user is following."""
        user = self.get_object()
        
        following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
        following_qs = User.objects.filter(id__in=following_ids)
        
        page = self.paginate_queryset(following_qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(following_qs, many=True)
        return Response(serializer.data)