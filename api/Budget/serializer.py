from rest_framework import serializers
from api.Budget.model import Budget


class BudgetSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    remaining_amount = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = ['id', 'user', 'username', 'bot', 'bot_name',
                  'allocated_amount', 'consumed_amount', 'remaining_amount',
                  'period_start', 'period_end', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_remaining_amount(self, obj):
        return obj.allocated_amount - obj.consumed_amount
