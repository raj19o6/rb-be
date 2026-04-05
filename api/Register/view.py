from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import Group
from django.utils import timezone
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

            # Grant ₹1000 welcome credit (bot=None, applies to all bots)
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

            return Response({
                **serializer.data,
                'welcome_credit': f'₹{WELCOME_CREDIT:.0f} credit added to your account.',
            }, status=201)
        return Response(serializer.errors, status=400)
