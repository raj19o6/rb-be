from rest_framework import serializers
from api.ResponsePrereq.model import ResponsePrereq


class ResponsePrereqSerializer(serializers.ModelSerializer):
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ResponsePrereq
        fields = ['id', 'bot', 'bot_name', 'user', 'username',
                  'key', 'value', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
