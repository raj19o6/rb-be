from rest_framework.viewsets import ModelViewSet
from api.Requests.model import Requests
from api.Requests.serializer import RequestsSerializer


class RequestsViewset(ModelViewSet):
    queryset = Requests.objects.select_related('requested_by', 'assigned_to').all()
    serializer_class = RequestsSerializer
