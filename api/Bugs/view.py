from rest_framework.viewsets import ModelViewSet
from api.Bugs.model import Bugs
from api.Bugs.serializer import BugsSerializer


class BugsViewset(ModelViewSet):
    queryset = Bugs.objects.select_related('bot', 'reported_by', 'assigned_to').all()
    serializer_class = BugsSerializer
