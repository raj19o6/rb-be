from rest_framework.viewsets import ModelViewSet
from api.Payment.model import Payment
from api.Payment.serializer import PaymentSerializer


class PaymentViewset(ModelViewSet):
    queryset = Payment.objects.select_related('billing', 'paid_by').all()
    serializer_class = PaymentSerializer
