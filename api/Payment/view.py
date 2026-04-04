from rest_framework.viewsets import ModelViewSet
from api.Payment.model import Payment
from api.Payment.serializer import PaymentSerializer


class PaymentViewset(ModelViewSet):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Payment.objects.select_related('billing', 'paid_by').all()
        return Payment.objects.select_related('billing', 'paid_by').filter(paid_by=user)
