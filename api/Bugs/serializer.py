from rest_framework import serializers
from api.Bugs.model import Bugs


class BugsSerializer(serializers.ModelSerializer):
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)

    class Meta:
        model = Bugs
        fields = ['id', 'bot', 'bot_name', 'title', 'description',
                  'severity', 'status', 'reported_by', 'reported_by_username',
                  'assigned_to', 'assigned_to_username', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
