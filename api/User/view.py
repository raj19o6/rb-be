from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from api.User.serializers import UserSerializer

User = get_user_model()


class UserViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
