from rest_framework.viewsets import ModelViewSet
from api.RequestsHistory.model import RequestsHistory
from api.RequestsHistory.serializer import RequestsHistorySerializer


class RequestsHistoryViewset(ModelViewSet):
    queryset = RequestsHistory.objects.select_related('request', 'changed_by').all()
    serializer_class = RequestsHistorySerializer
