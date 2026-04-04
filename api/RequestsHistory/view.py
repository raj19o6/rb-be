from rest_framework.viewsets import ModelViewSet
from api.RequestsHistory.model import RequestsHistory
from api.RequestsHistory.serializer import RequestsHistorySerializer


class RequestsHistoryViewset(ModelViewSet):
    serializer_class = RequestsHistorySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return RequestsHistory.objects.select_related('request', 'changed_by').all()
        return RequestsHistory.objects.select_related('request', 'changed_by').filter(
            request__requested_by=user
        )
