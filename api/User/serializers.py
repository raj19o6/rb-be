from rest_framework import serializers
from django.contrib.auth import get_user_model
from api.UserProfile.model import UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    contact_no = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name',
                  'groups', 'is_staff', 'is_active', 'contact_no']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            data['contact_no'] = instance.profile.contact_no
        except UserProfile.DoesNotExist:
            data['contact_no'] = None
        return data

    def _sync_permissions(self, user):
        from django.contrib.auth.models import Permission
        perms = Permission.objects.filter(group__user=user)
        user.user_permissions.set(perms)

    def create(self, validated_data):
        contact_no = validated_data.pop('contact_no', None)
        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        user.groups.set(groups)
        UserProfile.objects.create(user=user, contact_no=contact_no)
        self._sync_permissions(user)
        return user

    def update(self, instance, validated_data):
        contact_no = validated_data.pop('contact_no', None)
        groups = validated_data.pop('groups', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        if groups is not None:
            instance.groups.set(groups)
        profile, _ = UserProfile.objects.get_or_create(user=instance)
        if contact_no is not None:
            profile.contact_no = contact_no
            profile.save()
        self._sync_permissions(instance)
        return instance
