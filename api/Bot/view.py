from rest_framework.viewsets import ModelViewSet
from api.Bot.model import Bot
from api.Bot.serializer import BotSerializer


class BotViewset(ModelViewSet):
    queryset = Bot.objects.select_related('created_by').all()
    serializer_class = BotSerializer
