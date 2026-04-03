from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from api.BotMaintainance.model import BotMaintainance


class BotMaintainanceSerializer(serializers.ModelSerializer):
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = BotMaintainance
        fields = ['id', 'bot', 'bot_name', 'reason', 'started_at', 'ended_at',
                  'created_by', 'created_by_username', 'created_at']
        read_only_fields = ['created_by', 'created_at']


class ManageMaintenanceReason(APIView):
    def get(self, request):
        records = BotMaintainance.objects.filter(
            ended_at__isnull=True
        ).select_related('bot', 'created_by')
        serializer = BotMaintainanceSerializer(records, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BotMaintainanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
