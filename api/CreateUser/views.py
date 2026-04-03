from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.User.serializers import UserSerializer
from api.UserProfile.model import UserProfile


class CreateUserAPI(APIView):
    def get_permissions(self):
        return [IsAuthenticated()]

    def post(self, request):
        data = request.data.copy()
        data.setdefault('groups', [])
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            # Track who created this user
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if request.user and request.user.is_authenticated:
                profile.created_by = request.user
                profile.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
