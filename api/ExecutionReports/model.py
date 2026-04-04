import uuid
from django.db import models
from api.Executions.model import Executions


class ExecutionReports(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    execution = models.OneToOneField(Executions, on_delete=models.CASCADE, related_name='report')
    summary = models.TextField(blank=True, null=True)
    logs = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_execution_reports'

    def __str__(self):
        return f"Report for Execution {self.execution.id}"
