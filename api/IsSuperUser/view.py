from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class CheckUserType(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_type = 'superuser' if user.is_superuser else 'regular'
        roles = list(user.groups.values('id', 'name'))
        permissions = list(
            user.user_permissions.values('id', 'codename')
        )
        return Response({
            'user_type': user_type,
            'roles': roles,
            'permissions': permissions
        })
