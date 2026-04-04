from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from api.BotFunctions.model import BotFunctions
from api.BotFunctions.serializer import BotFunctionsSerializer


class BotFunctionsViewset(ModelViewSet):
    serializer_class = BotFunctionsSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return BotFunctions.objects.select_related('bot').all()
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'manager' in groups:
            return BotFunctions.objects.select_related('bot').all()
        return BotFunctions.objects.select_related('bot').filter(
            bot__allotments__user=user
        ).distinct()

    def perform_create(self, serializer):
        user = self.request.user
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'client' in groups:
            raise PermissionDenied('Clients have read-only access to bot functions.')
        serializer.save()
