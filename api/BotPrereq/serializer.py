from rest_framework import serializers
from api.BotPrereq.model import BotPrereq


class BotPrereqSerializer(serializers.ModelSerializer):
    bot_name = serializers.CharField(source='bot.name', read_only=True)

    class Meta:
        model = BotPrereq
        fields = ['id', 'bot', 'bot_name', 'name', 'description', 'is_required', 'created_at']
        read_only_fields = ['created_at']
