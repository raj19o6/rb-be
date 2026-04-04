from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from api.Requests.model import Requests
from api.Credentials.model import Credentials


class CredentialInlineSerializer(serializers.ModelSerializer):
    bot_name = serializers.CharField(source='bot.name', read_only=True)

    class Meta:
        model = Credentials
        fields = ['id', 'bot', 'bot_name', 'username', 'extra_data']


class RequestWithCredentialsSerializer(serializers.ModelSerializer):
    requested_by_username = serializers.CharField(source='requested_by.username', read_only=True)
    credentials = serializers.SerializerMethodField()

    class Meta:
        model = Requests
        fields = ['id', 'title', 'description', 'status', 'requested_by',
                  'requested_by_username', 'credentials', 'created_at', 'updated_at']

    def get_credentials(self, obj):
        user = obj.requested_by
        creds = Credentials.objects.filter(user=user).select_related('bot')
        return CredentialInlineSerializer(creds, many=True).data


class GetRequestWithCredentials(APIView):
    def get(self, request):
        requests_qs = Requests.objects.filter(
            requested_by=request.user
        ).select_related('requested_by')
        serializer = RequestWithCredentialsSerializer(requests_qs, many=True)
        return Response(serializer.data)
