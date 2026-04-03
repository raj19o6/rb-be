from rest_framework.viewsets import ModelViewSet
from api.BotMaintainance.model import BotMaintainance
from api.BotMaintainance.serializer import BotMaintainanceSerializer


class BotMaintainanceViewset(ModelViewSet):
    queryset = BotMaintainance.objects.select_related('bot', 'created_by').all()
    serializer_class = BotMaintainanceSerializer
