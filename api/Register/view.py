import os
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import Group
from api.User.serializers import UserSerializer

WELCOME_CREDIT = 1000.00


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.copy()
        data['groups']    = []
        data['is_staff']  = False
        data['is_active'] = True

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()

            # Assign client group
            try:
                client_group = Group.objects.get(name='client')
                user.groups.set([client_group])
            except Group.DoesNotExist:
                pass

            # Grant ₹1000 welcome credit
            from api.Billing.model import Billing
            today = timezone.now().date()
            Billing.objects.create(
                user=user,
                bot=None,
                amount=WELCOME_CREDIT,
                price_per_action=0.10,
                status='paid',
                billing_date=today,
                due_date=None,
            )

            # Send welcome email
            try:
                send_mail(
                    subject='Welcome to RichBot 🤖',
                    message='',
                    from_email=os.environ.get('EMAIL_HOST_USER'),
                    recipient_list=[user.email],
                    html_message=f"""
                    <div style="font-family:sans-serif;max-width:520px;margin:auto;padding:32px;background:#0f172a;color:#e2e8f0;border-radius:12px">
                        <h1 style="color:#6366f1;margin-bottom:8px">Welcome to RichBot! 🤖</h1>
                        <p style="color:#94a3b8;margin-bottom:24px">Hi <strong style="color:#f1f5f9">{user.username}</strong>, your account is ready.</p>
                        <div style="background:#1e293b;border-radius:8px;padding:20px;margin-bottom:24px">
                            <p style="margin:0 0 8px;color:#64748b;font-size:13px">WELCOME CREDIT</p>
                            <p style="margin:0;font-size:32px;font-weight:700;color:#22c55e">₹1,000</p>
                            <p style="margin:4px 0 0;color:#64748b;font-size:12px">Added to your account. Start running workflows today.</p>
                        </div>
                        <p style="color:#64748b;font-size:12px">If you did not create this account, please ignore this email.</p>
                    </div>
                    """,
                )
            except Exception:
                pass  # never block signup if email fails

            return Response({
                **serializer.data,
                'welcome_credit': f'₹{WELCOME_CREDIT:.0f} credit added to your account.',
            }, status=201)
        return Response(serializer.errors, status=400)
