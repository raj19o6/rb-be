from rest_framework.viewsets import ModelViewSet
from api.Budget.model import Budget
from api.Budget.serializer import BudgetSerializer


class BudgetViewset(ModelViewSet):
    serializer_class = BudgetSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Budget.objects.select_related('user', 'bot').all()
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
        if 'manager' in groups:
            from api.UserProfile.model import UserProfile
            client_ids = UserProfile.objects.filter(created_by=user).values_list('user_id', flat=True)
            return Budget.objects.select_related('user', 'bot').filter(user_id__in=client_ids)
        return Budget.objects.select_related('user', 'bot').filter(user=user)
