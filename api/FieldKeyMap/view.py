from rest_framework.viewsets import ModelViewSet
from api.FieldKeyMap.model import FieldKeyMap
from api.FieldKeyMap.serializer import FieldKeyMapSerializer


class FieldKeyMapViewset(ModelViewSet):
    queryset = FieldKeyMap.objects.select_related('field').all()
    serializer_class = FieldKeyMapSerializer
