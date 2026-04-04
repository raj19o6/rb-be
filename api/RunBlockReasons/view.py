from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from api.RunBlockReasons.model import RunBlockReasons
from api.RunBlockReasons.serializer import RunBlockReasonsSerializer


class RunBlockReasonsViewset(ModelViewSet):
    serializer_class = RunBlockReasonsSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return RunBlockReasons.objects.select_related('bot', 'user', 'created_by').all()
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'manager' in groups:
            return RunBlockReasons.objects.select_related('bot', 'user', 'created_by').all()
        return RunBlockReasons.objects.select_related('bot', 'user', 'created_by').filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'client' in groups:
            raise PermissionDenied('Clients cannot create run block reasons.')
        serializer.save(created_by=user)
