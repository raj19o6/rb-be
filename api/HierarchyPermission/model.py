import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import Permission


class UserPermissionAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='permissions_given'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='permissions_received'
    )
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('assigned_by', 'assigned_to', 'permission')

    def __str__(self):
        return f"{self.assigned_by} → {self.assigned_to} : {self.permission.codename}"
