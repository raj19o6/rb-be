from rest_framework import serializers
from api.RequestsHistory.model import RequestsHistory


class RequestsHistorySerializer(serializers.ModelSerializer):
    request_title = serializers.CharField(source='request.title', read_only=True)
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = RequestsHistory
        fields = ['id', 'request', 'request_title', 'changed_by', 'changed_by_username',
                  'previous_status', 'new_status', 'note', 'changed_at']
        read_only_fields = ['changed_at']
