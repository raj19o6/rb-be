from rest_framework.viewsets import ModelViewSet
from api.Workflow.model import Workflow
from api.Workflow.serializer import WorkflowSerializer


class WorkflowViewset(ModelViewSet):
    serializer_class = WorkflowSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Workflow.objects.select_related('created_by').all()
        return Workflow.objects.select_related('created_by').filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
