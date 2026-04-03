from rest_framework.viewsets import ModelViewSet
from api.Budget.model import Budget
from api.Budget.serializer import BudgetSerializer


class BudgetViewset(ModelViewSet):
    queryset = Budget.objects.select_related('user', 'bot').all()
    serializer_class = BudgetSerializer
