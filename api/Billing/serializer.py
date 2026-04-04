from rest_framework import serializers
from api.Billing.model import Billing


class BillingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    bot_name = serializers.CharField(source='bot.name', read_only=True)

    class Meta:
        model = Billing
        fields = ['id', 'user', 'username', 'bot', 'bot_name',
                  'amount', 'price_per_action', 'balance_remaining',
                  'status', 'billing_date', 'due_date', 'created_at']
        read_only_fields = ['balance_remaining', 'created_at']
