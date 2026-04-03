from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from api.BotAllotments.model import BotAllotments


class BotAllotmentsSerializer(serializers.ModelSerializer):
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    allotted_by_username = serializers.CharField(source='allotted_by.username', read_only=True)

    class Meta:
        model = BotAllotments
        fields = ['id', 'bot', 'bot_name', 'user', 'username', 'allotted_by', 'allotted_by_username', 'allotted_at']


class GetBotAllotmentsByUser(APIView):
    def get(self, request, user_id):
        allotments = BotAllotments.objects.filter(user_id=user_id).select_related('bot', 'user', 'allotted_by')
        serializer = BotAllotmentsSerializer(allotments, many=True)
        return Response(serializer.data)
