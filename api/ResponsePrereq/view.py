from rest_framework.viewsets import ModelViewSet
from api.ResponsePrereq.model import ResponsePrereq
from api.ResponsePrereq.serializer import ResponsePrereqSerializer


class ResponsePrereqViewset(ModelViewSet):
    queryset = ResponsePrereq.objects.select_related('bot', 'user').all()
    serializer_class = ResponsePrereqSerializer
