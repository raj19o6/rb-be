import os
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from api.Workflow.model import Workflow, WorkflowReport
from api.Workflow.serializer import WorkflowSerializer

API_BASE_URL = os.environ.get('API_BASE_URL', '')


class SaveWorkflowView(APIView):
    """POST /api/v1/workflows/save — Chrome extension saves workflow"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        workflow = Workflow.objects.create(
            workflow_name=data.get('workflowName'),
            session_id=data.get('sessionId'),
            actions=data.get('actions', []),
            metadata=data.get('metadata', {}),
            recorded_at=data.get('recordedAt'),
            action_count=data.get('actionCount', 0),
            created_by=request.user,
        )
        return Response({
            'workflow_id': str(workflow.id),
            'user_id': str(request.user.id),
            'username': request.user.username,
            'status': 'saved',
            'message': 'Workflow saved successfully'
        }, status=201)


class DownloadWorkflowView(APIView):
    """GET /api/v1/workflows/{workflow_id}/download — Jenkins downloads workflow JSON"""
    permission_classes = [AllowAny]

    def get(self, request, workflow_id):
        workflow = get_object_or_404(Workflow, id=workflow_id)
        return Response({
            'workflowName': workflow.workflow_name,
            'sessionId': workflow.session_id,
            'actions': workflow.actions,
            'metadata': workflow.metadata,
            'recordedAt': workflow.recorded_at,
            'actionCount': workflow.action_count,
        })


class ExecuteWorkflowView(APIView):
    """POST /api/v1/workflows/{workflow_id}/execute — sets status to queued, signal triggers Jenkins"""
    permission_classes = [IsAuthenticated]

    def post(self, request, workflow_id):
        workflow = get_object_or_404(Workflow, id=workflow_id)
        workflow.status = 'queued'
        workflow.save(update_fields=['status'])  # signal fires here

        report, _ = WorkflowReport.objects.get_or_create(workflow=workflow)
        return Response({
            'status': 'queued',
            'execution_id': str(report.id),
            'message': 'Workflow queued. Jenkins job triggered automatically.'
        })


class WorkflowReportView(APIView):
    """POST — Jenkins sends report back | GET — User views report"""

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def post(self, request, workflow_id):
        """Jenkins bot sends results back after execution"""
        workflow = get_object_or_404(Workflow, id=workflow_id)
        data = request.data

        report, _ = WorkflowReport.objects.get_or_create(workflow=workflow)
        report.status = data.get('status', 'completed')
        report.execution_time = data.get('execution_time')
        report.report_json = data.get('report', {})
        report.html_report = data.get('html_report', '')
        report.json_report = data.get('json_report', {})
        report.executed_at = timezone.now()

        # Save HTML as a file stored under reports/<user_id>/<username>/
        html_content = data.get('html_report', '')
        if html_content:
            from django.core.files.base import ContentFile
            user = workflow.created_by
            filename = f"{workflow.id}.html"
            report.html_report_file.save(filename, ContentFile(html_content.encode('utf-8')), save=False)

        report.save()

        workflow.status = data.get('status', 'completed')
        workflow.last_executed = timezone.now()
        workflow.save(update_fields=['status', 'last_executed'])

        return Response({
            'status': 'received',
            'report_id': str(report.id),
        })

    def get(self, request, workflow_id):
        """User views report in dashboard"""
        workflow = get_object_or_404(Workflow, id=workflow_id)
        report = get_object_or_404(WorkflowReport, workflow=workflow)

        summary = report.report_json.get('summary', {}) if report.report_json else {}
        total = summary.get('total', 0)
        passed = summary.get('passed', 0)
        success_rate = round((passed / total) * 100, 1) if total else None

        return Response({
            'workflow_id': str(workflow.id),
            'workflow_name': workflow.workflow_name,
            'user_id': str(workflow.created_by.id),
            'username': workflow.created_by.username,
            'status': report.status,
            'executed_at': report.executed_at,
            'execution_time': report.execution_time,
            'summary': {
                **summary,
                'success_rate': success_rate,
            },
            'html_report_url': request.build_absolute_uri(report.html_report_file.url) if report.html_report_file else None,
            'json_report_url': f"{API_BASE_URL}/api/v1/workflows/{workflow.id}/report/json/",
        })


class ListWorkflowsView(APIView):
    """GET /api/v1/workflows — Dashboard lists all workflows"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        qs = Workflow.objects.select_related('report').all() if user.is_superuser \
            else Workflow.objects.select_related('report').filter(created_by=user)

        workflows = []
        for wf in qs.order_by('-created_at'):
            summary = {}
            success_rate = None
            try:
                summary = wf.report.report_json.get('summary', {})
                total = summary.get('total', 0)
                passed = summary.get('passed', 0)
                success_rate = round((passed / total) * 100, 1) if total else None
            except Exception:
                pass

            workflows.append({
                'id': str(wf.id),
                'name': wf.workflow_name,
                'user_id': str(wf.created_by.id),
                'username': wf.created_by.username,
                'session_id': wf.session_id,
                'actions': wf.actions,
                'metadata': wf.metadata,
                'recorded_at': wf.recorded_at,
                'action_count': wf.action_count,
                'created_at': wf.created_at,
                'last_executed': wf.last_executed,
                'status': wf.status,
                'success_rate': success_rate,
            })

        return Response({'workflows': workflows})


class ServeHtmlReportView(APIView):
    """GET /api/v1/workflows/<id>/report/html/ — Serve HTML report file"""
    permission_classes = [IsAuthenticated]

    def get(self, request, workflow_id):
        workflow = get_object_or_404(Workflow, id=workflow_id)
        report = get_object_or_404(WorkflowReport, workflow=workflow)

        if not report.html_report_file:
            return Response({'error': 'HTML report not available yet.'}, status=404)

        from django.http import FileResponse
        return FileResponse(
            report.html_report_file.open('rb'),
            content_type='text/html',
            filename=f"{workflow.created_by.username}_{workflow.id}.html"
        )


class ServeJsonReportView(APIView):
    """GET /api/v1/workflows/<id>/report/json/ — Serve JSON report"""
    permission_classes = [IsAuthenticated]

    def get(self, request, workflow_id):
        workflow = get_object_or_404(Workflow, id=workflow_id)
        report = get_object_or_404(WorkflowReport, workflow=workflow)

        if not report.json_report:
            return Response({'error': 'JSON report not available yet.'}, status=404)

        return Response({
            'workflow_id': str(workflow.id),
            'workflow_name': workflow.workflow_name,
            'user_id': str(workflow.created_by.id),
            'username': workflow.created_by.username,
            'report': report.json_report,
        })
