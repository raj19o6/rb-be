from rest_framework import serializers
from django.contrib.auth import get_user_model
from api.UserProfile.model import UserProfile

User = get_user_model()


class GroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class UserDetailSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'groups']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'user_id', 'contact_no']
