from rest_framework import serializers
from api.Budget.history_model import BudgetHistory


class BudgetHistorySerializer(serializers.ModelSerializer):
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = BudgetHistory
        fields = '__all__'
