from rest_framework.viewsets import ModelViewSet
from api.BotAllotments.model import BotAllotments
from api.BotAllotments.serializer import BotAllotmentsSerializer


class BotAllotmentsViewset(ModelViewSet):
    queryset = BotAllotments.objects.select_related('bot', 'user', 'allotted_by').all()
    serializer_class = BotAllotmentsSerializer
