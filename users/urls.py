from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from users.views import UserRegistrationView, UserLogoutView, UserViewSet, UserInfoView

# Router for ViewSets
router = DefaultRouter()
router.register(r"profiles", UserViewSet, basename="profile")

urlpatterns = [
    # Auth endpoints
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", obtain_auth_token, name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("user_info/", UserInfoView.as_view(), name="current-user-info"),
    path("user_info/<int:pk>/", UserInfoView.as_view(), name="user-info-detail"),
    # Profile endpoints (list, retrieve, update)
    path("", include(router.urls)),
]
