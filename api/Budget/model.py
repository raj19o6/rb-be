import uuid
from django.db import models
from django.conf import settings
from api.Bot.model import Bot


class Budget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets'
    )
    bot = models.ForeignKey(Bot, null=True, blank=True, on_delete=models.SET_NULL, related_name='budgets')
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2)
    consumed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    period_start = models.DateField()
    period_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_budget'

    def __str__(self):
        return f"Budget for {self.user.username} ({self.period_start} - {self.period_end})"
