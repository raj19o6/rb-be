import uuid
from django.db import models
from api.Requests.model import Requests


class RequestFiles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(Requests, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='request_files/')
    file_name = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_request_files'

    def __str__(self):
        return f"File for {self.request.title}: {self.file_name}"
