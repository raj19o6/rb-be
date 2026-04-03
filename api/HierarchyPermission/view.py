from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from api.HierarchyPermission.model import UserPermissionAssignment
from api.HierarchyPermission.serializer import AssignPermissionSerializer, UserPermissionAssignmentSerializer

User = get_user_model()

ROLE_HIERARCHY = {
    'manager': 'client',
    'client': 'agent',
}


def get_user_role(user):
    groups = list(user.groups.values_list('name', flat=True))
    for role in ['manager', 'client', 'agent']:
        if role in groups:
            return role
    return None


def get_user_received_permissions(user):
    return UserPermissionAssignment.objects.filter(
        assigned_to=user
    ).values_list('permission_id', flat=True)


class AssignPermissionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AssignPermissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        assigner = request.user
        assignee = serializer.validated_data['assigned_to']
        permissions = serializer.validated_data['permissions']

        assigner_role = get_user_role(assigner)
        assignee_role = get_user_role(assignee)

        # Validate role hierarchy
        expected_assignee_role = ROLE_HIERARCHY.get(assigner_role)
        if not expected_assignee_role or assignee_role != expected_assignee_role:
            return Response(
                {'error': f'You can only assign permissions to a {expected_assignee_role}.'},
                status=403
            )

        # Validate assigner owns these permissions (unless manager/superuser)
        if not assigner.is_superuser and assigner_role != 'manager':
            allowed_perm_ids = set(get_user_received_permissions(assigner))
            for perm in permissions:
                if perm.id not in allowed_perm_ids:
                    return Response(
                        {'error': f'You do not have permission "{perm.codename}" to assign.'},
                        status=403
                    )

        # Assign permissions
        created = []
        for perm in permissions:
            obj, was_created = UserPermissionAssignment.objects.get_or_create(
                assigned_by=assigner,
                assigned_to=assignee,
                permission=perm
            )
            if was_created:
                created.append(perm.codename)
                # Also add to Django user permissions
                assignee.user_permissions.add(perm)

        return Response({
            'message': f'Assigned {len(created)} permission(s) to {assignee.username}.',
            'assigned': created
        })


class RevokePermissionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AssignPermissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        assigner = request.user
        assignee = serializer.validated_data['assigned_to']
        permissions = serializer.validated_data['permissions']

        revoked = []
        for perm in permissions:
            deleted, _ = UserPermissionAssignment.objects.filter(
                assigned_by=assigner,
                assigned_to=assignee,
                permission=perm
            ).delete()
            if deleted:
                assignee.user_permissions.remove(perm)
                revoked.append(perm.codename)

        return Response({
            'message': f'Revoked {len(revoked)} permission(s) from {assignee.username}.',
            'revoked': revoked
        })


class MyPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assignments = UserPermissionAssignment.objects.filter(assigned_to=request.user)
        serializer = UserPermissionAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)


class MyTeamView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = get_user_role(user)

        if role not in ROLE_HIERARCHY:
            return Response({'error': 'You do not manage any users.'}, status=403)

        # Get users created by this user
        from api.UserProfile.model import UserProfile
        created_profiles = UserProfile.objects.filter(created_by=user).select_related('user')

        team = []
        for profile in created_profiles:
            member = profile.user
            received_perms = UserPermissionAssignment.objects.filter(
                assigned_by=user, assigned_to=member
            ).values('permission__id', 'permission__codename', 'permission__name')
            team.append({
                'id': str(member.id),
                'username': member.username,
                'email': member.email,
                'role': get_user_role(member),
                'permissions_assigned': list(received_perms)
            })

        return Response(team)


class AssignmentListView(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPermissionAssignmentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return UserPermissionAssignment.objects.all()
        return UserPermissionAssignment.objects.filter(assigned_by=user)
