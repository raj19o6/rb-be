from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from api.Bugs.model import Bugs
from api.Bugs.serializer import BugsSerializer


class BugsViewset(ModelViewSet):
    serializer_class = BugsSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Bugs.objects.select_related('bot', 'reported_by', 'assigned_to')
        if user.is_superuser:
            return qs.all()
        # consistent with dashboard: show bugs reported by OR assigned to the user
        return qs.filter(Q(reported_by=user) | Q(assigned_to=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)
