from rest_framework import serializers
from api.FieldKeyMap.model import FieldKeyMap


class FieldKeyMapSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source='field.name', read_only=True)

    class Meta:
        model = FieldKeyMap
        fields = ['id', 'field', 'field_name', 'key', 'mapped_value', 'created_at']
        read_only_fields = ['created_at']
