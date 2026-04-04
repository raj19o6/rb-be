from django.urls import path
from security.views import CustomTokenObtainPairView, CustomTokenRefreshView, PasswordResetConfirmView

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view()),
    path('token/refresh/', CustomTokenRefreshView.as_view()),
    path('pass-reset/<str:temp_token>/', PasswordResetConfirmView.as_view()),
]
