from rest_framework.viewsets import ModelViewSet
from api.Billing.model import Billing
from api.Billing.serializer import BillingSerializer


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
            return Billing.objects.select_related('user', 'bot').filter(user_id__in=client_ids)
        return Billing.objects.select_related('user', 'bot').filter(user=user)
