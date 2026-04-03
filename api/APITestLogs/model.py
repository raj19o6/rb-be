import uuid
from django.db import models
from django.conf import settings


class APITestLogs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='api_test_logs'
    )
    endpoint = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    request_payload = models.JSONField(null=True, blank=True)
    response_payload = models.JSONField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    response_time_ms = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_test_logs'

    def __str__(self):
        return f"{self.method} {self.endpoint} ({self.status_code})"
