from rest_framework.viewsets import ModelViewSet
from api.Requests.model import Requests
from api.Requests.serializer import RequestsSerializer


class RequestsViewset(ModelViewSet):
    serializer_class = RequestsSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Requests.objects.select_related('requested_by', 'assigned_to').all()
        return Requests.objects.select_related('requested_by', 'assigned_to').filter(requested_by=user)

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)
