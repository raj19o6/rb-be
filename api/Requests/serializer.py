from rest_framework import serializers
from api.Requests.model import Requests


class RequestsSerializer(serializers.ModelSerializer):
    requested_by_username = serializers.CharField(source='requested_by.username', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    bot_name = serializers.CharField(source='bot.name', read_only=True)

    class Meta:
        model = Requests
        fields = ['id', 'bot', 'bot_name', 'title', 'description', 'status', 'rejection_reason',
                  'requested_by', 'requested_by_username',
                  'assigned_to', 'assigned_to_username',
                  'created_at', 'updated_at']
        read_only_fields = ['requested_by', 'status', 'rejection_reason', 'created_at', 'updated_at']
