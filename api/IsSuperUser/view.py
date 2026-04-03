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

        # Custom roles - show roles created by user OR roles whose permissions user has
        from api.HierarchyPermission.model import UserPermissionAssignment
        user_perm_ids = set(user.user_permissions.values_list('id', flat=True))
        custom_roles = CustomRole.objects.filter(
            permissions__id__in=user_perm_ids
        ).distinct()
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
