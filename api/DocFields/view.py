from rest_framework.viewsets import ModelViewSet
from api.DocFields.model import DocFields
from api.DocFields.serializer import DocFieldsSerializer


class DocFieldsViewset(ModelViewSet):
    queryset = DocFields.objects.select_related('category').all()
    serializer_class = DocFieldsSerializer
