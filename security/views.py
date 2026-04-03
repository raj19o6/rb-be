from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView
from security.serializers import CustomTokenRefreshSerializer

User = get_user_model()


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, temp_token):
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({'error': 'new_password is required'}, status=400)

        cached = cache.get(temp_token)
        if not cached:
            return Response({'error': 'Invalid or expired token'}, status=400)

        try:
            uid = urlsafe_base64_decode(cached['uid']).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, Exception):
            return Response({'error': 'Invalid token'}, status=400)

        if not default_token_generator.check_token(user, cached['token']):
            return Response({'error': 'Invalid or expired token'}, status=400)

        user.set_password(new_password)
        user.save()
        cache.delete(temp_token)
        return Response({'message': 'Password reset successful'})
