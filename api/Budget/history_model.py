import uuid
from django.db import models
from django.conf import settings
from api.Budget.model import Budget


class BudgetHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budget_history_changes'
    )
    previous_allocated = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    new_allocated = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    note = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_budget_history'

    def __str__(self):
        return f"BudgetHistory for {self.budget} at {self.changed_at}"
