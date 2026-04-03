from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class CheckUserType(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_type = 'superuser' if request.user.is_superuser else 'regular'
        return Response({'user_type': user_type})
