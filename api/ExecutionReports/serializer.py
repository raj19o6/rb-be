from rest_framework import serializers
from api.ExecutionReports.model import ExecutionReports


class ExecutionReportsSerializer(serializers.ModelSerializer):
    bot_name = serializers.CharField(source='execution.bot.name', read_only=True)
    executed_by_username = serializers.CharField(source='execution.executed_by.username', read_only=True)

    class Meta:
        model = ExecutionReports
        fields = ['id', 'execution', 'bot_name', 'executed_by_username',
                  'summary', 'logs', 'error_message', 'total_price', 'created_at']
        read_only_fields = ['created_at']
