import uuid
import os
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        User = get_user_model()
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'If this email exists, a reset link has been sent.'})

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        temp_token = str(uuid.uuid4())
        cache.set(temp_token, {'uid': uid, 'token': token}, timeout=3600)

        base_url = os.environ.get('BASE_URL', 'http://127.0.0.1:8000')
        reset_link = f"{base_url}/auth/pass-reset/{temp_token}/"

        send_mail(
            subject='Password Reset Request',
            message='',
            from_email=os.environ.get('EMAIL_HOST_USER'),
            recipient_list=[email],
            html_message=f'<p>Click <a href="{reset_link}">here</a> to reset your password. Link expires in 1 hour.</p>',
        )
        return Response({'message': 'If this email exists, a reset link has been sent.'})
