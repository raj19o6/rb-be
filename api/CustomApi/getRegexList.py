from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from api.Regex.model import Regex


class RegexSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Regex
        fields = ['id', 'name', 'pattern', 'description', 'created_by', 'created_by_username',
                  'created_at', 'updated_at']


class GetRegexList(APIView):
    def get(self, request):
        qs = Regex.objects.select_related('created_by').all()

        name = request.query_params.get('name')
        if name:
            qs = qs.filter(name__icontains=name)

        serializer = RegexSerializer(qs, many=True)
        return Response(serializer.data)
