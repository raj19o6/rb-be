from rest_framework.viewsets import ModelViewSet
from api.ExecutionReports.model import ExecutionReports
from api.ExecutionReports.serializer import ExecutionReportsSerializer


class ExecutionReportsViewset(ModelViewSet):
    serializer_class = ExecutionReportsSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ExecutionReports.objects.select_related('execution__bot', 'execution__executed_by').all()
        return ExecutionReports.objects.select_related('execution__bot', 'execution__executed_by').filter(
            execution__executed_by=user
        )
