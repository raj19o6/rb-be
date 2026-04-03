from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from api.User.serializers import UserSerializer

User = get_user_model()


class UserViewset(ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()

        user_groups = [g.lower() for g in user.groups.values_list('name', flat=True)]

        if 'manager' in user_groups:
            return User.objects.filter(is_superuser=False)

        if 'client' in user_groups:
            return User.objects.filter(is_superuser=False).exclude(
                groups__name__iexact='manager'
            )

        if 'agent' in user_groups:
            return User.objects.filter(is_superuser=False).exclude(
                groups__name__iexact='manager'
            ).exclude(
                groups__name__iexact='client'
            )

        return User.objects.filter(is_superuser=False)
