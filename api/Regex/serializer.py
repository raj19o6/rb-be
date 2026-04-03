from rest_framework import serializers
from api.Regex.model import Regex


class RegexSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Regex
        fields = ['id', 'name', 'pattern', 'description',
                  'created_by', 'created_by_username', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
