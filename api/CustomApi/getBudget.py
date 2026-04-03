from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from api.Budget.model import Budget


class BudgetSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    remaining_amount = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = ['id', 'user', 'username', 'bot', 'bot_name', 'allocated_amount',
                  'consumed_amount', 'remaining_amount', 'period_start', 'period_end',
                  'created_at', 'updated_at']

    def get_remaining_amount(self, obj):
        return obj.allocated_amount - obj.consumed_amount


class GetBudget(APIView):
    def get(self, request):
        qs = Budget.objects.filter(user=request.user).select_related('user', 'bot')

        bot_id = request.query_params.get('bot_id')
        if bot_id:
            qs = qs.filter(bot_id=bot_id)

        serializer = BudgetSerializer(qs, many=True)
        return Response(serializer.data)
