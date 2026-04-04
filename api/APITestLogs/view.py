from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from api.APITestLogs.model import APITestLogs
from api.APITestLogs.serializer import APITestLogsSerializer


class APITestLogsViewset(ModelViewSet):
    serializer_class = APITestLogsSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return APITestLogs.objects.select_related('user').all()
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'manager' in groups:
            return APITestLogs.objects.select_related('user').all()
        return APITestLogs.objects.select_related('user').filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
