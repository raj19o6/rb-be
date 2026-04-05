from rest_framework import serializers
from api.ExecutionReports.model import ExecutionReports


class ExecutionReportsSerializer(serializers.ModelSerializer):
    bot_name            = serializers.CharField(source='execution.bot.name', read_only=True)
    executed_by_username = serializers.CharField(source='execution.executed_by.username', read_only=True)
    executed_by_email   = serializers.CharField(source='execution.executed_by.email', read_only=True)
    execution_status    = serializers.CharField(source='execution.status', read_only=True)
    started_at          = serializers.DateTimeField(source='execution.started_at', read_only=True)
    ended_at            = serializers.DateTimeField(source='execution.ended_at', read_only=True)
    request_title       = serializers.CharField(source='execution.request.title', read_only=True)
    workflow_name       = serializers.SerializerMethodField()

    class Meta:
        model = ExecutionReports
        fields = [
            'id', 'execution', 'bot_name',
            'executed_by_username', 'executed_by_email',
            'execution_status', 'started_at', 'ended_at',
            'request_title', 'workflow_name',
            'summary', 'logs', 'error_message', 'total_price', 'created_at',
        ]
        read_only_fields = ['created_at']

    def get_workflow_name(self, obj):
        from api.Workflow.model import Workflow
        wf = Workflow.objects.filter(
            metadata__execution_id=str(obj.execution.id)
        ).only('workflow_name').first()
        return wf.workflow_name if wf else None
