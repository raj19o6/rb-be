from rest_framework import serializers
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from api.HierarchyPermission.model import UserPermissionAssignment

User = get_user_model()


class AssignPermissionSerializer(serializers.Serializer):
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True)


class UserPermissionAssignmentSerializer(serializers.ModelSerializer):
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    permission_codename = serializers.CharField(source='permission.codename', read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)

    class Meta:
        model = UserPermissionAssignment
        fields = ['id', 'assigned_by', 'assigned_by_username', 'assigned_to',
                  'assigned_to_username', 'permission', 'permission_codename',
                  'permission_name', 'created_at']
