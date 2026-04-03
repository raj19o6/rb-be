from rest_framework import serializers
from api.APITestLogs.model import APITestLogs


class APITestLogsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = APITestLogs
        fields = ['id', 'user', 'username', 'endpoint', 'method',
                  'request_payload', 'response_payload', 'status_code',
                  'response_time_ms', 'created_at']
        read_only_fields = ['created_at']
