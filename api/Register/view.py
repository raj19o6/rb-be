from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import Group
from api.User.serializers import UserSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.copy()
        data['groups'] = []
        data['is_staff'] = False
        data['is_active'] = True

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            try:
                client_group = Group.objects.get(name='client')
                user.groups.set([client_group])
            except Group.DoesNotExist:
                pass
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
