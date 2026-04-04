from rest_framework.viewsets import ModelViewSet
from api.Notification.model import Notification
from api.Notification.serializer import NotificationSerializer


class NotificationViewset(ModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Notification.objects.select_related('user').all()
        return Notification.objects.select_related('user').filter(user=user)
