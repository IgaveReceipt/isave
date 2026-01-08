from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from igaveapp.views import UserViewSet, ReceiptViewSet, CustomTokenObtainPairView

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"receipts", ReceiptViewSet, basename="receipt")

urlpatterns = [
    path("admin/", admin.site.urls),

    # API
    path("api/", include(router.urls)),

    # JWT auth (THIS FIXES CI)
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("api/register/", UserViewSet.as_view({'post': 'create'}), name="register"), 
]
