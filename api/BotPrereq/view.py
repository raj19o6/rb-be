from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from api.BotPrereq.model import BotPrereq
from api.BotPrereq.serializer import BotPrereqSerializer


class BotPrereqViewset(ModelViewSet):
    serializer_class = BotPrereqSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return BotPrereq.objects.select_related('bot').all()
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'manager' in groups:
            return BotPrereq.objects.select_related('bot').all()
        return BotPrereq.objects.select_related('bot').filter(
            bot__allotments__user=user
        ).distinct()

    def perform_create(self, serializer):
        user = self.request.user
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'client' in groups:
            raise PermissionDenied('Clients have read-only access to bot prerequisites.')
        serializer.save()
