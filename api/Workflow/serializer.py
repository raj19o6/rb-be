from rest_framework import serializers
from api.Workflow.model import Workflow, WorkflowReport


class WorkflowReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowReport
        fields = ['id', 'status', 'execution_time', 'report_json',
                  'html_report', 'json_report', 'executed_at', 'created_at']


class WorkflowSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    success_rate = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = ['id', 'workflow_name', 'session_id', 'actions', 'metadata',
                  'recorded_at', 'action_count', 'status', 'last_executed',
                  'created_by', 'created_by_username', 'success_rate', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'status', 'last_executed', 'created_at', 'updated_at']

    def get_success_rate(self, obj):
        try:
            summary = obj.report.report_json.get('summary', {})
            total = summary.get('total', 0)
            passed = summary.get('passed', 0)
            return round((passed / total) * 100, 1) if total else None
        except Exception:
            return None
