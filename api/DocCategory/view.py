from rest_framework.viewsets import ModelViewSet
from api.DocCategory.model import DocCategory
from api.DocCategory.serializer import DocCategorySerializer


class DocCategoryViewset(ModelViewSet):
    queryset = DocCategory.objects.select_related('created_by').all()
    serializer_class = DocCategorySerializer
