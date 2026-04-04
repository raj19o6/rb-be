from rest_framework.viewsets import ModelViewSet
from api.ExecutionReports.model import ExecutionReports
from api.ExecutionReports.serializer import ExecutionReportsSerializer


class ExecutionReportsViewset(ModelViewSet):
    queryset = ExecutionReports.objects.select_related('execution__bot', 'execution__executed_by').all()
    serializer_class = ExecutionReportsSerializer
