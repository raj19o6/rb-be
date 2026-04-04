from rest_framework.viewsets import ModelViewSet
from api.BotAllotments.model import BotAllotments
from api.BotAllotments.serializer import BotAllotmentsSerializer


class BotAllotmentsViewset(ModelViewSet):
    serializer_class = BotAllotmentsSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return BotAllotments.objects.select_related('bot', 'user', 'allotted_by').all()
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'manager' in groups:
            return BotAllotments.objects.select_related('bot', 'user', 'allotted_by').filter(
                allotted_by=user
            )
        return BotAllotments.objects.select_related('bot', 'user', 'allotted_by').filter(
            user=user
        )

    def perform_create(self, serializer):
        serializer.save(allotted_by=self.request.user)
