from rest_framework import serializers
from api.Credentials.model import Credentials


class CredentialsSerializer(serializers.ModelSerializer):
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    username_display = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Credentials
        fields = ['id', 'bot', 'bot_name', 'user', 'username_display',
                  'username', 'password', 'extra_data', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}
