from rest_framework.viewsets import ModelViewSet
from api.RunBlockReasons.model import RunBlockReasons
from api.RunBlockReasons.serializer import RunBlockReasonsSerializer


class RunBlockReasonsViewset(ModelViewSet):
    queryset = RunBlockReasons.objects.select_related('bot', 'user', 'created_by').all()
    serializer_class = RunBlockReasonsSerializer
