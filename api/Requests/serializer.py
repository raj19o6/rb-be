from rest_framework import serializers
from api.Requests.model import Requests


class RequestsSerializer(serializers.ModelSerializer):
    requested_by_username = serializers.CharField(source='requested_by.username', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)

    class Meta:
        model = Requests
        fields = ['id', 'title', 'description', 'status',
                  'requested_by', 'requested_by_username',
                  'assigned_to', 'assigned_to_username',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
