from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from api.ResponsePrereq.model import ResponsePrereq


class ResponsePrereqSerializer(serializers.ModelSerializer):
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ResponsePrereq
        fields = ['id', 'bot', 'bot_name', 'user', 'username', 'key', 'value', 'created_at', 'updated_at']


class GetResponsePrereqByUser(APIView):
    def get(self, request, user_id):
        prereqs = ResponsePrereq.objects.filter(user_id=user_id).select_related('bot', 'user')
        serializer = ResponsePrereqSerializer(prereqs, many=True)
        return Response(serializer.data)
