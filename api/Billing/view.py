from rest_framework.viewsets import ModelViewSet
from api.Billing.model import Billing
from api.Billing.serializer import BillingSerializer


class BillingViewset(ModelViewSet):
    queryset = Billing.objects.select_related('user', 'bot').all()
    serializer_class = BillingSerializer
