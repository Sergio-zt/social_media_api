from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from users.views import UserRegistrationView, UserLogoutView, UserViewSet

# Router for ViewSets
router = DefaultRouter()
router.register(r"profiles", UserViewSet, basename="profile")

urlpatterns = [
    # Auth endpoints
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", obtain_auth_token, name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    # Profile endpoints (list, retrieve, update)
    path("", include(router.urls)),
]
