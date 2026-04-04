from rest_framework.viewsets import ModelViewSet
from api.Regex.model import Regex
from api.Regex.serializer import RegexSerializer


class RegexViewset(ModelViewSet):
    queryset = Regex.objects.select_related('created_by').all()
    serializer_class = RegexSerializer
