from rest_framework import serializers
from api.DocFields.model import DocFields


class DocFieldsSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = DocFields
        fields = ['id', 'category', 'category_name', 'name', 'field_type', 'is_required', 'created_at']
        read_only_fields = ['created_at']
