from rest_framework.viewsets import ModelViewSet
from api.RequestFiles.model import RequestFiles
from api.RequestFiles.serializer import RequestFilesSerializer


class RequestFilesViewset(ModelViewSet):
    serializer_class = RequestFilesSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return RequestFiles.objects.select_related('request').all()
        return RequestFiles.objects.select_related('request').filter(
            request__requested_by=user
        )
