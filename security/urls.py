from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from security.views import CustomTokenRefreshView, PasswordResetConfirmView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', CustomTokenRefreshView.as_view()),
    path('pass-reset/<str:temp_token>/', PasswordResetConfirmView.as_view()),
]
