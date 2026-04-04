from rest_framework import serializers
from api.BotFunctions.model import BotFunctions


class BotFunctionsSerializer(serializers.ModelSerializer):
    bot_name = serializers.CharField(source='bot.name', read_only=True)

    class Meta:
        model = BotFunctions
        fields = ['id', 'bot', 'bot_name', 'name', 'description', 'function_key', 'created_at']
        read_only_fields = ['created_at']
