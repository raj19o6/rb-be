from rest_framework.viewsets import ModelViewSet
from api.ResponsePrereq.model import ResponsePrereq
from api.ResponsePrereq.serializer import ResponsePrereqSerializer


class ResponsePrereqViewset(ModelViewSet):
    serializer_class = ResponsePrereqSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ResponsePrereq.objects.select_related('bot', 'user').all()
        return ResponsePrereq.objects.select_related('bot', 'user').filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
