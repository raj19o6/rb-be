from rest_framework import serializers
from api.BotAllotments.model import BotAllotments


class BotAllotmentsSerializer(serializers.ModelSerializer):
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    allotted_by_username = serializers.SerializerMethodField()

    class Meta:
        model = BotAllotments
        fields = ['id', 'bot', 'bot_name', 'user', 'username',
                  'allotted_by', 'allotted_by_username', 'allotted_at']
        read_only_fields = ['allotted_by', 'allotted_at']

    def get_allotted_by_username(self, obj):
        return obj.allotted_by.username if obj.allotted_by else None
