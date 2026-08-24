from rest_framework import status, viewsets, mixins, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from users.serializers import UserRegistrationSerializer, UserSerializer
from users.permissions import IsOwnerOrReadOnly

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
    - We use mixins to prevent creation via this endpoint (registration handles that).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    # Adding search capabilities
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'bio']  # Allows searching by email or bio