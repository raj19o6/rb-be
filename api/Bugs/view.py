from rest_framework.viewsets import ModelViewSet
from api.Bugs.model import Bugs
from api.Bugs.serializer import BugsSerializer


class BugsViewset(ModelViewSet):
    serializer_class = BugsSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Bugs.objects.select_related('bot', 'reported_by', 'assigned_to').all()
        return Bugs.objects.select_related('bot', 'reported_by', 'assigned_to').filter(reported_by=user)

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)
