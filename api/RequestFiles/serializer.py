from rest_framework import serializers
from api.RequestFiles.model import RequestFiles


class RequestFilesSerializer(serializers.ModelSerializer):
    request_title = serializers.CharField(source='request.title', read_only=True)

    class Meta:
        model = RequestFiles
        fields = ['id', 'request', 'request_title', 'file', 'file_name', 'uploaded_at']
        read_only_fields = ['uploaded_at']
