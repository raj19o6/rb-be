from rest_framework import serializers
from api.Executions.model import Executions


class ExecutionsSerializer(serializers.ModelSerializer):
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    executed_by_username = serializers.CharField(source='executed_by.username', read_only=True)
    request_title = serializers.CharField(source='request.title', read_only=True)

    class Meta:
        model = Executions
        fields = ['id', 'bot', 'bot_name', 'request', 'request_title',
                  'executed_by', 'executed_by_username', 'status',
                  'started_at', 'ended_at', 'created_at']
        read_only_fields = ['executed_by', 'status', 'started_at', 'ended_at', 'created_at']
