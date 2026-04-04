from rest_framework.viewsets import ModelViewSet
from api.APITestLogs.model import APITestLogs
from api.APITestLogs.serializer import APITestLogsSerializer


class APITestLogsViewset(ModelViewSet):
    queryset = APITestLogs.objects.select_related('user').all()
    serializer_class = APITestLogsSerializer
