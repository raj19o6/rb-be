from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from decimal import Decimal
from api.Billing.model import Billing
from api.Billing.serializer import BillingSerializer

WELCOME_CREDIT = Decimal('1000.00')


class BillingViewset(ModelViewSet):
    serializer_class = BillingSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Billing.objects.select_related('user', 'bot').all()
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'manager' in groups:
            from api.UserProfile.model import UserProfile
            client_ids = UserProfile.objects.filter(created_by=user).values_list('user_id', flat=True)
            return Billing.objects.select_related('user', 'bot').filter(
                user_id__in=client_ids, status='paid'
            )
        # Regular clients only see their active paid billing with remaining balance
        return Billing.objects.select_related('user', 'bot').filter(
            user=user, status='paid'
        )

    @action(detail=False, methods=['post'], url_path='cleanup', permission_classes=[IsAuthenticated])
    def cleanup(self, request):
        """POST /api/v1/billing/cleanup/ — superuser removes garbage unpaid/zero records"""
        if not request.user.is_superuser:
            return Response({'error': 'Only superusers can run cleanup.'}, status=403)
        deleted, _ = Billing.objects.filter(status='unpaid', amount=0).delete()
        return Response({'deleted': deleted, 'message': f'{deleted} garbage billing record(s) removed.'})

    @action(detail=False, methods=['post'], url_path='top_up', permission_classes=[IsAuthenticated])
    def top_up(self, request):
        """POST /api/v1/billing/top_up/ — superuser tops up any user's balance"""
        if not request.user.is_superuser:
            return Response({'error': 'Only superusers can top up.'}, status=403)

        user_id = request.data.get('user_id')
        amount  = request.data.get('amount')
        if not user_id or not amount:
            return Response({'error': 'user_id and amount are required.'}, status=400)

        from django.contrib.auth import get_user_model
        from django.db.models import F
        User = get_user_model()
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

        billing = Billing.objects.filter(user=target_user, bot=None, status='paid').first()
        if billing:
            billing.balance_remaining = F('balance_remaining') + Decimal(str(amount))
            billing.amount            = F('amount') + Decimal(str(amount))
            billing.save(update_fields=['balance_remaining', 'amount'])
            billing.refresh_from_db()
        else:
            billing = Billing.objects.create(
                user=target_user,
                bot=None,
                amount=Decimal(str(amount)),
                price_per_action=Decimal('0.10'),
                status='paid',
                billing_date=timezone.now().date(),
            )

        return Response({
            'user':              target_user.username,
            'amount_added':      str(amount),
            'balance_remaining': str(billing.balance_remaining),
        })

    @action(detail=False, methods=['post'], url_path='grant_welcome_credit', permission_classes=[IsAuthenticated])
    def grant_welcome_credit(self, request):
        """POST /api/v1/billing/grant_welcome_credit/ — backfill welcome credit for existing users"""
        if not request.user.is_superuser:
            return Response({'error': 'Only superusers can grant credits.'}, status=403)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        today = timezone.now().date()
        granted = []
        skipped = []

        for user in User.objects.filter(is_superuser=False, is_active=True):
            exists = Billing.objects.filter(user=user, bot=None, status='paid').exists()
            if not exists:
                Billing.objects.create(
                    user=user,
                    bot=None,
                    amount=WELCOME_CREDIT,
                    price_per_action=Decimal('0.10'),
                    status='paid',
                    billing_date=today,
                )
                granted.append(user.username)
            else:
                skipped.append(user.username)

        return Response({
            'granted': granted,
            'skipped': skipped,
            'message': f'{len(granted)} users credited, {len(skipped)} already had credit.',
        })
