from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group
from api.Role.serializer import RoleSerializer


class RoleViewset(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = RoleSerializer
