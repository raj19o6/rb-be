from rest_framework.viewsets import ModelViewSet
from api.BotFunctions.model import BotFunctions
from api.BotFunctions.serializer import BotFunctionsSerializer


class BotFunctionsViewset(ModelViewSet):
    queryset = BotFunctions.objects.select_related('bot').all()
    serializer_class = BotFunctionsSerializer
