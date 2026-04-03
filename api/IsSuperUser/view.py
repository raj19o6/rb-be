from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.CustomRole.model import CustomRole


class CheckUserType(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_type = 'superuser' if user.is_superuser else 'regular'

        # System roles (Django groups)
        system_roles = list(user.groups.values('id', 'name'))
        for role in system_roles:
            role['type'] = 'system'

        # Custom roles assigned to this user via permissions
        custom_roles = CustomRole.objects.filter(created_by=user)
        custom_role_list = [
            {'id': str(r.id), 'name': r.name, 'type': 'custom'}
            for r in custom_roles
        ]

        permissions = list(user.user_permissions.values('id', 'codename'))

        return Response({
            'user_type': user_type,
            'roles': system_roles + custom_role_list,
            'permissions': permissions
        })
