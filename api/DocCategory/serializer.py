from rest_framework import serializers
from api.DocCategory.model import DocCategory


class DocCategorySerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = DocCategory
        fields = ['id', 'name', 'description', 'created_by', 'created_by_username',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
