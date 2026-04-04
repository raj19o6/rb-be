from rest_framework.viewsets import ModelViewSet
from api.UserProfile.model import UserProfile
from api.UserProfile.serializers import UserProfileSerializer


class UserProfileViewset(ModelViewSet):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return UserProfile.objects.select_related('user').all()
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'manager' in groups:
            return UserProfile.objects.select_related('user').filter(created_by=user)
        return UserProfile.objects.select_related('user').filter(user=user)
