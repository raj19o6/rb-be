from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from api.Bot.model import Bot
from api.Bot.serializer import BotSerializer


class BotViewset(ModelViewSet):
    serializer_class = BotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Bot.objects.select_related('created_by').all()
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'manager' in groups:
            return Bot.objects.select_related('created_by').all()
        # Client sees only allotted bots
        return Bot.objects.select_related('created_by').filter(
            allotments__user=user
        ).distinct()

    def http_method_not_allowed(self, request, *args, **kwargs):
        user = request.user
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'client' in groups and request.method not in ('GET', 'HEAD', 'OPTIONS'):
            from rest_framework.response import Response
            return Response({'error': 'Clients have read-only access to bots.'}, status=403)
        return super().http_method_not_allowed(request, *args, **kwargs)
