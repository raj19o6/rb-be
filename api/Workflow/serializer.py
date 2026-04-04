from rest_framework import serializers
from api.Workflow.model import Workflow


class WorkflowSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Workflow
        fields = ['id', 'name', 'description', 'workflow_json',
                  'created_by', 'created_by_username', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']
