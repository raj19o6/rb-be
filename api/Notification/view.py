from rest_framework.viewsets import ModelViewSet
from api.Notification.model import Notification
from api.Notification.serializer import NotificationSerializer


class NotificationViewset(ModelViewSet):
    queryset = Notification.objects.select_related('user').all()
    serializer_class = NotificationSerializer
