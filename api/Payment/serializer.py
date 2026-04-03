from rest_framework import serializers
from api.Payment.model import Payment


class PaymentSerializer(serializers.ModelSerializer):
    paid_by_username = serializers.CharField(source='paid_by.username', read_only=True)
    billing_status = serializers.CharField(source='billing.status', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'billing', 'billing_status', 'paid_by', 'paid_by_username',
                  'amount', 'transaction_id', 'method', 'status', 'paid_at', 'created_at']
        read_only_fields = ['created_at']
