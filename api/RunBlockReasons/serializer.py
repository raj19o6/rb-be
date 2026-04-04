from rest_framework import serializers
from api.RunBlockReasons.model import RunBlockReasons


class RunBlockReasonsSerializer(serializers.ModelSerializer):
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = RunBlockReasons
        fields = ['id', 'bot', 'bot_name', 'user', 'username',
                  'reason', 'is_active', 'created_by', 'created_by_username',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
