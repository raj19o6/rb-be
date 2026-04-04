from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from api.Executions.model import Executions
from api.Executions.serializer import ExecutionsSerializer


class ExecutionsViewset(ModelViewSet):
    serializer_class = ExecutionsSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Executions.objects.select_related('bot', 'request', 'executed_by').all()
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'manager' in groups:
            from api.UserProfile.model import UserProfile
            client_ids = UserProfile.objects.filter(created_by=user).values_list('user_id', flat=True)
            return Executions.objects.select_related('bot', 'request', 'executed_by').filter(
                executed_by_id__in=client_ids
            )
        return Executions.objects.select_related('bot', 'request', 'executed_by').filter(
            executed_by=user
        )

    def perform_create(self, serializer):
        user = self.request.user
        bot = serializer.validated_data.get('bot')

        # Check paid billing exists for this user + bot
        from api.Billing.model import Billing
        has_paid = Billing.objects.filter(user=user, bot=bot, status='paid').exists()
        if not has_paid:
            raise PermissionDenied('You have not paid for this bot. Please complete payment first.')

        serializer.save(executed_by=user)
