from rest_framework import serializers
from api.BotMaintainance.model import BotMaintainance


class BotMaintainanceSerializer(serializers.ModelSerializer):
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = BotMaintainance
        fields = ['id', 'bot', 'bot_name', 'reason', 'started_at', 'ended_at',
                  'created_by', 'created_by_username', 'created_at']
        read_only_fields = ['created_at']
