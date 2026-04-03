import uuid
from django.db import models
from api.DocFields.model import DocFields


class FieldKeyMap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field = models.ForeignKey(DocFields, on_delete=models.CASCADE, related_name='key_maps')
    key = models.CharField(max_length=255)
    mapped_value = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_field_key_map'

    def __str__(self):
        return f"{self.key} → {self.mapped_value} (field: {self.field.name})"
