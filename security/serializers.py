from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['user_id'] = str(user.id)
        token['username'] = user.username
        token['email'] = user.email
        token['is_superuser'] = user.is_superuser

        # Role (manager / client)
        groups = list(user.groups.values_list('name', flat=True))
        token['role'] = next(
            (r for r in ['manager', 'client'] if r in [g.lower() for g in groups]),
            'superuser' if user.is_superuser else None
        )
        token['groups'] = groups



        return token


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken(attrs['refresh'])
        data['refresh'] = str(refresh)
        return data
