from rest_framework.viewsets import ModelViewSet
from api.Credentials.model import Credentials
from api.Credentials.serializer import CredentialsSerializer


class CredentialsViewset(ModelViewSet):
    queryset = Credentials.objects.select_related('bot', 'user').all()
    serializer_class = CredentialsSerializer
