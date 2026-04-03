import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import Permission


class CustomRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_roles'
    )
    permissions = models.ManyToManyField(Permission, blank=True, related_name='custom_roles')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'created_by')

    def __str__(self):
        return f"{self.name} (by {self.created_by.username})"
