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
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    credential = CredentialInlineSerializer(read_only=True)

    class Meta:
        model = Requests
        fields = [
            'id', 'title', 'description', 'status',
            'bot', 'bot_name',
            'requested_by', 'requested_by_username',
            'credential', 'created_at', 'updated_at'
        ]


class GetRequestWithCredentials(APIView):
    def get(self, request):
        user = request.user
        if user.is_superuser:
            qs = Requests.objects.select_related(
                'requested_by', 'bot', 'credential'
            ).all()
        else:
            groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
            if 'manager' in groups:
                from api.UserProfile.model import UserProfile
                client_ids = UserProfile.objects.filter(created_by=user).values_list('user_id', flat=True)
                qs = Requests.objects.select_related(
                    'requested_by', 'bot', 'credential'
                ).filter(requested_by_id__in=client_ids)
            else:
                qs = Requests.objects.select_related(
                    'requested_by', 'bot', 'credential'
                ).filter(requested_by=user)

        serializer = RequestWithCredentialsSerializer(qs, many=True)
        return Response(serializer.data)
