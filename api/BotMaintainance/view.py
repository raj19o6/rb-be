from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from api.BotMaintainance.model import BotMaintainance
from api.BotMaintainance.serializer import BotMaintainanceSerializer


class BotMaintainanceViewset(ModelViewSet):
    serializer_class = BotMaintainanceSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return BotMaintainance.objects.select_related('bot', 'created_by').all()
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'manager' in groups:
            return BotMaintainance.objects.select_related('bot', 'created_by').all()
        return BotMaintainance.objects.select_related('bot', 'created_by').filter(
            bot__allotments__user=user
        ).distinct()

    def perform_create(self, serializer):
        user = self.request.user
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'client' in groups:
            raise PermissionDenied('Clients have read-only access to bot maintenance.')
        serializer.save(created_by=user)
