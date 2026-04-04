from rest_framework import serializers
from api.Requests.model import Requests


class CredentialSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField()
    extra_data = serializers.JSONField()


class RequestsSerializer(serializers.ModelSerializer):
    requested_by_username = serializers.CharField(source='requested_by.username', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    credential_detail = serializers.SerializerMethodField()

    class Meta:
        model = Requests
        fields = [
            'id', 'bot', 'bot_name', 'credential', 'credential_detail',
            'title', 'description', 'status', 'rejection_reason',
            'requested_by', 'requested_by_username',
            'assigned_to', 'assigned_to_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['requested_by', 'status', 'rejection_reason', 'created_at', 'updated_at']

    def get_credential_detail(self, obj):
        if not obj.credential:
            return None
        return CredentialSummarySerializer(obj.credential).data

    def validate(self, data):
        bot = data.get('bot')
        credential = data.get('credential')
        # If credential provided, ensure it belongs to the same bot
        if credential and bot and credential.bot_id != bot.id:
            raise serializers.ValidationError(
                {'credential': 'Credential does not belong to the selected bot.'}
            )
        return data
