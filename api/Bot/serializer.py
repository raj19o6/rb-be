from rest_framework import serializers
from api.Bot.model import Bot


class BotSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Bot
        fields = ['id', 'name', 'description', 'status',
                  'created_by', 'created_by_username', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
