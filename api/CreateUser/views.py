from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.User.serializers import UserSerializer
from api.UserProfile.model import UserProfile
from api.CustomRole.model import CustomRole
from api.HierarchyPermission.model import UserPermissionAssignment


class CreateUserAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data.setdefault('groups', [])
        custom_role_id = data.pop('custom_role', None)

        # Validate custom_role belongs to the requesting user
        custom_role = None
        if custom_role_id:
            try:
                custom_role = CustomRole.objects.get(
                    id=custom_role_id,
                    created_by=request.user
                )
            except CustomRole.DoesNotExist:
                return Response(
                    {'error': 'Custom role not found or does not belong to you.'},
                    status=400
                )

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()

            # Set created_by in profile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.created_by = request.user
            profile.save()

            # Assign custom role permissions to user
            if custom_role:
                for perm in custom_role.permissions.all():
                    # Add to Django user permissions
                    user.user_permissions.add(perm)
                    # Track in UserPermissionAssignment
                    UserPermissionAssignment.objects.get_or_create(
                        assigned_by=request.user,
                        assigned_to=user,
                        permission=perm
                    )

            response_data = serializer.data
            response_data['custom_role'] = {
                'id': str(custom_role.id),
                'name': custom_role.name,
                'permissions': list(custom_role.permissions.values('id', 'codename'))
            } if custom_role else None

            return Response(response_data, status=201)
        return Response(serializer.errors, status=400)
