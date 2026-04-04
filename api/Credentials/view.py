from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from api.Credentials.model import Credentials
from api.Credentials.serializer import CredentialsSerializer


class CredentialsViewset(ModelViewSet):
    serializer_class = CredentialsSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Credentials.objects.select_related('bot', 'user').all()
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'manager' in groups:
            from api.UserProfile.model import UserProfile
            client_ids = UserProfile.objects.filter(created_by=user).values_list('user_id', flat=True)
            return Credentials.objects.select_related('bot', 'user').filter(user_id__in=client_ids)
        return Credentials.objects.select_related('bot', 'user').filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'manager' in groups and not user.is_superuser:
            raise PermissionDenied('Managers cannot create credentials on behalf of clients.')
        serializer.save(user=user)
