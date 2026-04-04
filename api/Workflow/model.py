import uuid
from django.db import models
from django.conf import settings


class Workflow(models.Model):
    STATUS_CHOICES = [
        ('saved', 'Saved'),
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_name = models.CharField(max_length=255)
    session_id = models.CharField(max_length=255, unique=True)
    actions = models.JSONField()
    metadata = models.JSONField(blank=True, null=True)
    recorded_at = models.DateTimeField(null=True, blank=True)
    action_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='saved')
    last_executed = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workflows'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_workflow'

    def __str__(self):
        return self.workflow_name


def report_upload_path(instance, filename):
    user = instance.workflow.created_by
    return f"reports/{user.id}/{user.username}/{filename}"


class WorkflowReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.OneToOneField(Workflow, on_delete=models.CASCADE, related_name='report')
    status = models.CharField(max_length=20, default='pending')
    execution_time = models.FloatField(null=True, blank=True)
    report_json = models.JSONField(null=True, blank=True)
    html_report = models.TextField(null=True, blank=True)
    html_report_file = models.FileField(upload_to=report_upload_path, null=True, blank=True)
    json_report = models.JSONField(null=True, blank=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_workflow_report'

    def __str__(self):
        return f"Report for {self.workflow.workflow_name}"
