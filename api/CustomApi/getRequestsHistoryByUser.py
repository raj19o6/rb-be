from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from api.RequestsHistory.model import RequestsHistory


class RequestsHistorySerializer(serializers.ModelSerializer):
    request_title = serializers.CharField(source='request.title', read_only=True)
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = RequestsHistory
        fields = ['id', 'request', 'request_title', 'changed_by', 'changed_by_username',
                  'previous_status', 'new_status', 'note', 'changed_at']


class GetRequestsHistoryByUser(APIView):
    def get(self, request, user_id):
        history = RequestsHistory.objects.filter(changed_by_id=user_id).select_related('request', 'changed_by')
        serializer = RequestsHistorySerializer(history, many=True)
        return Response(serializer.data)
