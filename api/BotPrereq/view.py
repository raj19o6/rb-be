from rest_framework.viewsets import ModelViewSet
from api.BotPrereq.model import BotPrereq
from api.BotPrereq.serializer import BotPrereqSerializer


class BotPrereqViewset(ModelViewSet):
    queryset = BotPrereq.objects.select_related('bot').all()
    serializer_class = BotPrereqSerializer
