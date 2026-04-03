from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group
from api.Role.serializer import RoleSerializer

# What roles each role can see/assign
ROLE_VISIBILITY = {
    'manager': ['client', 'agent'],
    'client': ['agent'],
    'agent': [],
}


class RoleViewset(ModelViewSet):
    serializer_class = RoleSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Group.objects.all()

        user_groups = list(user.groups.values_list('name', flat=True))

        for role in ['manager', 'client', 'agent']:
            if role in user_groups:
                visible = ROLE_VISIBILITY.get(role, [])
                return Group.objects.filter(name__in=visible)

        return Group.objects.none()
