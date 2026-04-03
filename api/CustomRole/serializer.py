from rest_framework import serializers
from django.contrib.auth.models import Permission
from api.CustomRole.model import CustomRole
from api.HierarchyPermission.model import UserPermissionAssignment


class CustomRoleSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(), many=True, required=False
    )
    permission_details = serializers.SerializerMethodField()

    class Meta:
        model = CustomRole
        fields = ['id', 'name', 'created_by', 'created_by_username',
                  'permissions', 'permission_details', 'created_at']
        read_only_fields = ['created_by', 'created_at']

    def get_permission_details(self, obj):
        return list(obj.permissions.values('id', 'codename', 'name'))

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        permissions = attrs.get('permissions', [])

        if not user.is_superuser:
            # Get permissions assigned to this user
            allowed_perm_ids = set(
                UserPermissionAssignment.objects.filter(
                    assigned_to=user
                ).values_list('permission_id', flat=True)
            )
            for perm in permissions:
                if perm.id not in allowed_perm_ids:
                    raise serializers.ValidationError(
                        {'permissions': f'You do not have permission "{perm.codename}" to include in this role.'}
                    )
        return attrs

    def create(self, validated_data):
        permissions = validated_data.pop('permissions', [])
        role = CustomRole.objects.create(
            created_by=self.context['request'].user,
            **validated_data
        )
        role.permissions.set(permissions)
        return role

    def update(self, instance, validated_data):
        permissions = validated_data.pop('permissions', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if permissions is not None:
            instance.permissions.set(permissions)
        return instance
