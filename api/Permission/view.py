from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission
from api.Permission.serializer import PermissionSerializer


EXCLUDED_CONTENT_TYPES = [
    'session', 'blacklistedtoken', 'outstandingtoken',
    'logentry', 'contenttype', 'permission'
]


class PermissionViewset(ModelViewSet):
    serializer_class = PermissionSerializer

    def get_queryset(self):
        return Permission.objects.exclude(
            content_type__model__in=EXCLUDED_CONTENT_TYPES
        )
