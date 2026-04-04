from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from api.BotAllotments.model import BotAllotments


class BotAllotmentsSerializer(serializers.ModelSerializer):
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    allotted_by_username = serializers.SerializerMethodField()

    class Meta:
        model = BotAllotments
        fields = ['id', 'bot', 'bot_name', 'user', 'username', 'allotted_by', 'allotted_by_username', 'allotted_at']

    def get_allotted_by_username(self, obj):
        return obj.allotted_by.username if obj.allotted_by else None


class GetBotAllotmentsByUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        # Non-superusers can only view their own allotments
        if not request.user.is_superuser and str(request.user.id) != str(user_id):
            return Response({'error': 'You can only view your own bot allotments.'}, status=403)

        allotments = BotAllotments.objects.filter(user_id=user_id).select_related('bot', 'user', 'allotted_by')
        serializer = BotAllotmentsSerializer(allotments, many=True)
        return Response(serializer.data)
