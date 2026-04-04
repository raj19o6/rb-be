from rest_framework.viewsets import ModelViewSet
from api.Executions.model import Executions
from api.Executions.serializer import ExecutionsSerializer


class ExecutionsViewset(ModelViewSet):
    queryset = Executions.objects.select_related('bot', 'request', 'executed_by').all()
    serializer_class = ExecutionsSerializer
