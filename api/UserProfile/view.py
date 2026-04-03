from rest_framework.viewsets import ModelViewSet
from api.UserProfile.model import UserProfile
from api.UserProfile.serializers import UserProfileSerializer


class UserProfileViewset(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
