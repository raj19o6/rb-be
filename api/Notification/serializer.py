from rest_framework import serializers
from api.Notification.model import Notification


class NotificationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'username', 'title', 'message',
                  'notification_type', 'is_read', 'created_at']
        read_only_fields = ['created_at']
