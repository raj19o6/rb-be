from rest_framework.viewsets import ModelViewSet
from api.RequestFiles.model import RequestFiles
from api.RequestFiles.serializer import RequestFilesSerializer


class RequestFilesViewset(ModelViewSet):
    queryset = RequestFiles.objects.select_related('request').all()
    serializer_class = RequestFilesSerializer
