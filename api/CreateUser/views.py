from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from api.User.serializers import UserSerializer


class CreateUserAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.copy()
        data.setdefault('groups', [])
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
