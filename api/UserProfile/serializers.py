from rest_framework import serializers
from api.UserProfile.model import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['contact_no']
