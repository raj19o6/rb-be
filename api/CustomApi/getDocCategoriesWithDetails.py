from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from api.DocCategory.model import DocCategory
from api.DocFields.model import DocFields
from api.FieldKeyMap.model import FieldKeyMap


class FieldKeyMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldKeyMap
        fields = ['id', 'key', 'mapped_value', 'created_at']


class DocFieldsSerializer(serializers.ModelSerializer):
    key_maps = FieldKeyMapSerializer(many=True, read_only=True)

    class Meta:
        model = DocFields
        fields = ['id', 'name', 'field_type', 'is_required', 'key_maps', 'created_at']


class DocCategoryWithDetailsSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    fields = DocFieldsSerializer(many=True, read_only=True)

    class Meta:
        model = DocCategory
        fields = ['id', 'name', 'description', 'created_by', 'created_by_username',
                  'fields', 'created_at', 'updated_at']


class GetDocCategoriesWithDetails(APIView):
    def get(self, request):
        categories = DocCategory.objects.prefetch_related(
            'fields__key_maps'
        ).select_related('created_by').all()
        serializer = DocCategoryWithDetailsSerializer(categories, many=True)
        return Response(serializer.data)
