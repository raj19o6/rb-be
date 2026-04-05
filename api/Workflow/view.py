import os
from decimal import Decimal
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from api.Workflow.model import Workflow, WorkflowReport

API_BASE_URL = os.environ.get('API_BASE_URL', '')


class SaveWorkflowView(APIView):
    """POST /api/v1/workflows/save — Chrome extension saves workflow"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data   = request.data
        bot_id = data.get('botId')

        bot = None
        if bot_id:
            from api.Bot.model import Bot
            bot = Bot.objects.filter(id=bot_id).first()
            if not bot:
                return Response({'error': 'Bot not found.'}, status=400)

        try:
            workflow = Workflow.objects.create(
                bot=bot,
                workflow_name=data.get('workflowName'),
                session_id=data.get('sessionId'),
                actions=data.get('actions', []),
                metadata=data.get('metadata', {}),
                recorded_at=data.get('recordedAt'),
                action_count=data.get('actionCount', 0),
                created_by=request.user,
            )
        except Exception:
            # session_id already exists — update instead
            workflow = Workflow.objects.get(session_id=data.get('sessionId'))
            workflow.workflow_name = data.get('workflowName', workflow.workflow_name)
            workflow.actions       = data.get('actions', workflow.actions)
            workflow.action_count  = data.get('actionCount', workflow.action_count)
            workflow.metadata      = data.get('metadata', workflow.metadata)
            workflow.bot           = bot or workflow.bot
            workflow.status        = 'saved'
            workflow.save()

        return Response({
            'workflow_id': str(workflow.id),
            'user_id':     str(request.user.id),
            'username':    request.user.username,
            'bot_id':      str(bot.id) if bot else None,
            'bot_name':    bot.name if bot else None,
            'status':      'saved',
            'message':     'Workflow saved successfully'
        }, status=201)


class DownloadWorkflowView(APIView):
    """GET /api/v1/workflows/{workflow_id}/download — Jenkins downloads workflow JSON"""
    permission_classes = [AllowAny]

    def get(self, request, workflow_id):
        workflow = get_object_or_404(Workflow, id=workflow_id)
        return Response({
            'workflowName': workflow.workflow_name,
            'sessionId':    workflow.session_id,
            'actions':      workflow.actions,
            'metadata':     workflow.metadata,
            'recordedAt':   workflow.recorded_at,
            'actionCount':  workflow.action_count,
        })


class ExecuteWorkflowView(APIView):
    """POST /api/v1/workflows/{workflow_id}/execute"""
    permission_classes = [IsAuthenticated]

    def post(self, request, workflow_id):
        from api.Billing.model import Billing
        from api.Requests.model import Requests

        workflow = get_object_or_404(Workflow, id=workflow_id, created_by=request.user)
        user = request.user

        if not workflow.bot:
            return Response({
                'error': 'No bot linked to this workflow.',
                'code':  'NO_BOT'
            }, status=400)

        bot = workflow.bot

        approved_request = Requests.objects.filter(
            requested_by=user, bot=bot, status='approved'
        ).first()
        if not approved_request:
            pending = Requests.objects.filter(
                requested_by=user, bot=bot, status='pending'
            ).first()
            if pending:
                return Response({
                    'error': f'Your request for {bot.name} is still pending approval.',
                    'code':  'REQUEST_PENDING',
                    'request_id': str(pending.id)
                }, status=403)
            return Response({
                'error':     f'You have not requested access to {bot.name}.',
                'code':      'NO_REQUEST',
                'next_step': 'POST /api/v1/requests/'
            }, status=403)

        # bot-specific billing first, fall back to welcome credit (bot=None)
        billing = (
            Billing.objects.filter(user=user, bot=bot, status='paid').first() or
            Billing.objects.filter(user=user, bot=None, status='paid').first()
        )
        if not billing:
            unpaid = Billing.objects.filter(user=user, bot=bot, status='unpaid').first()
            if unpaid:
                return Response({
                    'error':      f'Please complete payment to run {bot.name}.',
                    'code':       'PAYMENT_REQUIRED',
                    'billing_id': str(unpaid.id),
                    'amount_due': str(unpaid.amount),
                    'next_step':  'POST /api/v1/payment/'
                }, status=402)
            return Response({
                'error': f'No billing found for {bot.name}. Contact your manager.',
                'code':  'NO_BILLING'
            }, status=403)

        cost = Decimal(str(workflow.action_count)) * billing.price_per_action
        if billing.balance_remaining < cost:
            return Response({
                'error':     'Insufficient balance to run this workflow.',
                'code':      'INSUFFICIENT_BALANCE',
                'required':  str(cost),
                'available': str(billing.balance_remaining),
                'shortfall': str(cost - billing.balance_remaining),
            }, status=402)

        # All checks passed — queue the workflow
        workflow.status = 'queued'
        workflow.save(update_fields=['status'])

        report, _ = WorkflowReport.objects.get_or_create(
            workflow=workflow,
            defaults={'status': 'queued'}
        )

        return Response({
            'status':        'queued',
            'workflow_id':   str(workflow.id),
            'report_id':     str(report.id),
            'bot':           bot.name,
            'cost':          str(cost),
            'balance_after': str(billing.balance_remaining - cost),
            'report_url':    f'/api/v1/workflows/{workflow.id}/report/',
            'message':       'Workflow queued. Jenkins job triggered automatically.'
        })


class WorkflowReportView(APIView):
    """POST — Jenkins sends report back | GET — User views report"""

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def post(self, request, workflow_id):
        """Jenkins bot sends results back after execution"""
        from django.db.models import F
        from api.Billing.model import Billing

        workflow = get_object_or_404(Workflow, id=workflow_id)
        data     = request.data

        report, _ = WorkflowReport.objects.get_or_create(workflow=workflow)
        report.status         = data.get('status', 'completed')
        report.execution_time = data.get('execution_time')
        report.report_json    = data.get('report', {})
        report.html_report    = data.get('report_html', '') or data.get('html_report', '')
        report.json_report    = data.get('report', {})
        report.executed_at    = timezone.now()

        html_content = data.get('report_html', '') or data.get('html_report', '')
        if html_content:
            from django.core.files.base import ContentFile
            filename = f"{workflow.id}.html"
            report.html_report_file.save(
                filename, ContentFile(html_content.encode('utf-8')), save=False
            )
        report.save()

        final_status = data.get('status', 'completed')
        workflow.status       = final_status
        workflow.last_executed = timezone.now()

        if final_status == 'completed':
            # Increment execution counter and total actions consumed
            workflow.execution_count        = F('execution_count') + 1
            workflow.total_actions_consumed = F('total_actions_consumed') + workflow.action_count

            # Deduct cost from billing (bot-specific first, fall back to welcome credit)
            billing = (
                Billing.objects.filter(user=workflow.created_by, bot=workflow.bot, status='paid').first() or
                Billing.objects.filter(user=workflow.created_by, bot=None, status='paid').first()
            )
            if billing:
                cost = Decimal(str(workflow.action_count)) * billing.price_per_action
                billing.balance_remaining = max(
                    Decimal('0'), billing.balance_remaining - cost
                )
                billing.save(update_fields=['balance_remaining'])

        workflow.save(update_fields=[
            'status', 'last_executed', 'execution_count', 'total_actions_consumed'
        ])

        return Response({'status': 'received', 'report_id': str(report.id)})

    def get(self, request, workflow_id):
        """User views report — ?format=html or ?format=json or default summary"""
        workflow = get_object_or_404(Workflow, id=workflow_id)
        report   = WorkflowReport.objects.filter(workflow=workflow).first()

        if not report:
            return Response({
                'workflow_id':   str(workflow.id),
                'workflow_name': workflow.workflow_name,
                'status':        workflow.status,
                'message':       'Report not available yet.'
            }, status=200)

        fmt = request.query_params.get('format')

        if fmt == 'html':
            if not report.html_report_file:
                return Response({'error': 'HTML report not available yet.'}, status=404)
            from django.http import FileResponse
            return FileResponse(
                report.html_report_file.open('rb'),
                content_type='text/html',
                filename=f"{workflow.created_by.username}_{workflow.id}.html"
            )

        if fmt == 'json':
            if not report.json_report:
                return Response({'error': 'JSON report not available yet.'}, status=404)
            return Response({
                'workflow_id':   str(workflow.id),
                'workflow_name': workflow.workflow_name,
                'user_id':       str(workflow.created_by.id),
                'username':      workflow.created_by.username,
                'report':        report.json_report,
            })

        summary      = report.report_json.get('summary', {}) if report.report_json else {}
        total        = summary.get('total', 0)
        passed       = summary.get('passed', 0)
        success_rate = round((passed / total) * 100, 1) if total else None

        return Response({
            'workflow_id':       str(workflow.id),
            'workflow_name':     workflow.workflow_name,
            'user_id':           str(workflow.created_by.id),
            'username':          workflow.created_by.username,
            'execution_count':   workflow.execution_count,
            'total_actions_consumed': workflow.total_actions_consumed,
            'status':            report.status,
            'executed_at':       report.executed_at,
            'execution_time':    report.execution_time,
            'report':            report.report_json,
            'html_report':       report.html_report,
            'json_report':       report.json_report,
            'summary':           {**summary, 'success_rate': success_rate},
            'html_report_url':   request.build_absolute_uri(report.html_report_file.url) if report.html_report_file else None,
            'json_report_url':   f"{request.build_absolute_uri(f'/api/v1/workflows/{workflow.id}/report/')}?format=json",
        })


class WorkflowDetailView(APIView):
    """GET, PATCH, DELETE /api/v1/workflows/<id>/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, workflow_id):
        workflow = get_object_or_404(Workflow, id=workflow_id, created_by=request.user)
        report   = WorkflowReport.objects.filter(workflow=workflow).first()
        return Response({
            'id':                     str(workflow.id),
            'name':                   workflow.workflow_name,
            'user_id':                str(workflow.created_by.id),
            'username':               workflow.created_by.username,
            'session_id':             workflow.session_id,
            'actions':                workflow.actions,
            'metadata':               workflow.metadata,
            'recorded_at':            workflow.recorded_at,
            'action_count':           workflow.action_count,
            'execution_count':        workflow.execution_count,
            'total_actions_consumed': workflow.total_actions_consumed,
            'status':                 workflow.status,
            'last_executed':          workflow.last_executed,
            'created_at':             workflow.created_at,
            'has_report':             report is not None,
        })

    def patch(self, request, workflow_id):
        workflow = get_object_or_404(Workflow, id=workflow_id, created_by=request.user)
        data = request.data
        if 'workflowName' in data:
            workflow.workflow_name = data['workflowName']
        if 'actions' in data:
            workflow.actions      = data['actions']
            workflow.action_count = len(data['actions'])
        if 'metadata' in data:
            workflow.metadata = data['metadata']
        workflow.save()
        return Response({'message': 'Workflow updated.', 'id': str(workflow.id)})

    def delete(self, request, workflow_id):
        workflow = get_object_or_404(Workflow, id=workflow_id, created_by=request.user)
        workflow.delete()
        return Response({'message': 'Workflow deleted.'}, status=204)


class ListWorkflowsView(APIView):
    """GET /api/v1/workflows — lists all workflows"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user   = request.user
        groups = [g.lower() for g in user.groups.values_list('name', flat=True)]

        if user.is_superuser:
            qs = Workflow.objects.select_related('bot', 'created_by', 'report').all()
        elif 'manager' in groups:
            from api.UserProfile.model import UserProfile
            client_ids = UserProfile.objects.filter(created_by=user).values_list('user_id', flat=True)
            qs = Workflow.objects.select_related('bot', 'created_by', 'report').filter(
                created_by_id__in=client_ids
            )
        else:
            qs = Workflow.objects.select_related('bot', 'created_by', 'report').filter(
                created_by=user
            )

        workflows = []
        for wf in qs.order_by('-created_at'):
            success_rate = None
            try:
                rj    = wf.report.report_json or {}
                s     = rj.get('summary', {})
                total = s.get('total', 0)
                success_rate = round((s.get('passed', 0) / total) * 100, 1) if total else None
            except Exception:
                pass

            workflows.append({
                'id':                     str(wf.id),
                'name':                   wf.workflow_name,
                'user_id':                str(wf.created_by.id),
                'username':               wf.created_by.username,
                'bot_id':                 str(wf.bot.id) if wf.bot else None,
                'bot_name':               wf.bot.name if wf.bot else None,
                'session_id':             wf.session_id,
                'action_count':           wf.action_count,
                'execution_count':        wf.execution_count,
                'total_actions_consumed': wf.total_actions_consumed,
                'status':                 wf.status,
                'last_executed':          wf.last_executed,
                'created_at':             wf.created_at,
                'success_rate':           success_rate,
                'has_report':             hasattr(wf, 'report') and wf.report is not None,
            })

        return Response({'count': len(workflows), 'workflows': workflows})
