from rest_framework.viewsets import ModelViewSet
from api.Credentials.model import Credentials
from api.Credentials.serializer import CredentialsSerializer


class CredentialsViewset(ModelViewSet):
    serializer_class = CredentialsSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Credentials.objects.select_related('bot', 'user').all()
        return Credentials.objects.select_related('bot', 'user').filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
