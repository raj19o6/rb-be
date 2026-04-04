from rest_framework.viewsets import ModelViewSet
from api.Budget.model import Budget
from api.Budget.serializer import BudgetSerializer


class BudgetViewset(ModelViewSet):
    serializer_class = BudgetSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Budget.objects.select_related('user', 'bot').all()
        return Budget.objects.select_related('user', 'bot').filter(user=user)
