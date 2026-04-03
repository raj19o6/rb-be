from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from api.CustomRole.model import CustomRole
from api.CustomRole.serializer import CustomRoleSerializer


class CustomRoleViewset(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomRoleSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return CustomRole.objects.all()
        # Only see roles you created
        return CustomRole.objects.filter(created_by=user)
