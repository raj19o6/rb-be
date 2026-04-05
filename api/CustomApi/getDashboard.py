from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q, F
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

from api.Bot.model import Bot
from api.BotAllotments.model import BotAllotments
from api.Executions.model import Executions
from api.Budget.model import Budget
from api.Billing.model import Billing
from api.Bugs.model import Bugs
from api.Requests.model import Requests
from api.Notification.model import Notification
from api.CustomRole.model import CustomRole
from api.Workflow.model import Workflow, WorkflowReport


class GetDashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        is_super = user.is_superuser

        # ── Users & Roles (superuser only) ───────────────────────────────────
        users_roles = None
        if is_super:
            User = get_user_model()
            user_qs = User.objects.all()
            users_roles = {
                "users": {
                    "total":      user_qs.count(),
                    "active":     user_qs.filter(is_active=True).count(),
                    "inactive":   user_qs.filter(is_active=False).count(),
                    "superusers": user_qs.filter(is_superuser=True).count(),
                },
                "roles": {
                    "system_roles": Group.objects.count(),
                    "custom_roles": CustomRole.objects.count(),
                    "total":        Group.objects.count() + CustomRole.objects.count(),
                },
            }

        # ── Bots ─────────────────────────────────────────────────────────────
        # FIX: use correct related_name 'allotments' confirmed from BotAllotments model
        bot_qs = Bot.objects.all() if is_super else Bot.objects.filter(allotments__user=user).distinct()
        bot_status = bot_qs.aggregate(
            active=Count('id', filter=Q(status='active')),
            inactive=Count('id', filter=Q(status='inactive')),
            maintenance=Count('id', filter=Q(status='maintenance')),
        )
        bots = {"total": bot_qs.count(), **bot_status}

        # ── Executions ───────────────────────────────────────────────────────
        # Mirror exact 3-tier scoping from ExecutionsViewset
        if is_super:
            exec_qs = Executions.objects.all()
        else:
            groups = [g.lower() for g in user.groups.values_list('name', flat=True)]
            if 'manager' in groups:
                from api.UserProfile.model import UserProfile
                client_ids = UserProfile.objects.filter(created_by=user).values_list('user_id', flat=True)
                exec_qs = Executions.objects.filter(executed_by_id__in=client_ids)
            else:
                exec_qs = Executions.objects.filter(executed_by=user)

        exec_agg = exec_qs.aggregate(
            success=Count('id',   filter=Q(status='success')),
            failed=Count('id',    filter=Q(status='failed')),
            running=Count('id',   filter=Q(status='running')),
            queued=Count('id',    filter=Q(status='queued')),
            cancelled=Count('id', filter=Q(status='cancelled')),
        )

        exec_by_bot = list(
            exec_qs
            .values('bot__id', 'bot__name')
            .annotate(
                total=Count('id'),
                success=Count('id',   filter=Q(status='success')),
                failed=Count('id',    filter=Q(status='failed')),
                running=Count('id',   filter=Q(status='running')),
                queued=Count('id',    filter=Q(status='queued')),
                cancelled=Count('id', filter=Q(status='cancelled')),
            )
            .order_by('-total')
        )

        recent_executions = list(
            exec_qs
            .order_by('-created_at')[:10]
            .values(
                'id', 'status', 'started_at', 'ended_at', 'created_at',
                'bot__id', 'bot__name',
                'request__id', 'request__title',
                'executed_by__id', 'executed_by__username', 'executed_by__email',
            )
        )

        executions = {
            "total": exec_qs.count(),
            "by_status": {
                "success":   exec_agg['success'],
                "failed":    exec_agg['failed'],
                "running":   exec_agg['running'],
                "queued":    exec_agg['queued'],
                "cancelled": exec_agg['cancelled'],
            },
            "by_bot": [
                {
                    "bot_id":    str(r['bot__id']),
                    "bot_name":  r['bot__name'],
                    "total":     r['total'],
                    "success":   r['success'],
                    "failed":    r['failed'],
                    "running":   r['running'],
                    "queued":    r['queued'],
                    "cancelled": r['cancelled'],
                }
                for r in exec_by_bot
            ],
            "recent": [
                {
                    "id":                str(r['id']),
                    "status":            r['status'],
                    "bot_id":            str(r['bot__id']),
                    "bot_name":          r['bot__name'],
                    "request_id":        str(r['request__id']) if r['request__id'] else None,
                    "request_title":     r['request__title'],
                    "executed_by_id":    str(r['executed_by__id']),
                    "executed_by":       r['executed_by__username'],
                    "executed_by_email": r['executed_by__email'],
                    "started_at":        r['started_at'].isoformat() if r['started_at'] else None,
                    "ended_at":          r['ended_at'].isoformat() if r['ended_at'] else None,
                    "created_at":        r['created_at'].isoformat(),
                }
                for r in recent_executions
            ],
        }

        # ── Budget ───────────────────────────────────────────────────────────
        budget_qs = Budget.objects.all() if is_super else Budget.objects.filter(user=user)
        budget_agg = budget_qs.aggregate(
            total_allocated=Sum('allocated_amount'),
            total_consumed=Sum('consumed_amount'),
        )
        allocated = budget_agg['total_allocated'] or 0
        consumed  = budget_agg['total_consumed'] or 0
        budget = {
            "total_allocated": float(allocated),
            "total_consumed":  float(consumed),
            "total_remaining": float(allocated - consumed),
        }

        # ── Billing ──────────────────────────────────────────────────────────
        # FIX: single query with conditional aggregation instead of 3 separate queries
        billing_qs = Billing.objects.all() if is_super else Billing.objects.filter(user=user)
        billing_agg = billing_qs.aggregate(
            total_amount=Sum('amount'),
            paid=Sum('amount', filter=Q(status='paid')),
            unpaid=Sum('amount', filter=Q(status='unpaid')),
            overdue=Sum('amount', filter=Q(status='overdue')),
            total_balance_remaining=Sum('balance_remaining'),
        )
        billing = {k: float(v) if v else 0 for k, v in billing_agg.items()}

        # ── Bugs ─────────────────────────────────────────────────────────────
        bugs_qs = Bugs.objects.all() if is_super else Bugs.objects.filter(
            Q(reported_by=user) | Q(assigned_to=user)
        ).distinct()

        bugs_agg = bugs_qs.aggregate(
            open=Count('id', filter=Q(status='open')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            resolved=Count('id', filter=Q(status='resolved')),
            closed=Count('id', filter=Q(status='closed')),
            # open+in_progress severity breakdown
            low=Count('id',      filter=Q(severity='low',      status__in=['open', 'in_progress'])),
            medium=Count('id',   filter=Q(severity='medium',   status__in=['open', 'in_progress'])),
            high=Count('id',     filter=Q(severity='high',     status__in=['open', 'in_progress'])),
            critical=Count('id', filter=Q(severity='critical', status__in=['open', 'in_progress'])),
            # per-bot bug counts
        )

        # Bugs grouped by bot
        bugs_by_bot = list(
            bugs_qs
            .values('bot__id', 'bot__name')
            .annotate(
                total=Count('id'),
                open=Count('id',      filter=Q(status='open')),
                in_progress=Count('id', filter=Q(status='in_progress')),
                resolved=Count('id',  filter=Q(status='resolved')),
                critical=Count('id',  filter=Q(severity='critical', status__in=['open', 'in_progress'])),
                high=Count('id',      filter=Q(severity='high',     status__in=['open', 'in_progress'])),
            )
            .order_by('-total')
        )

        # Recent open/in_progress bugs with full detail
        recent_bugs = list(
            bugs_qs
            .filter(status__in=['open', 'in_progress'])
            .order_by('-created_at')[:10]
            .values(
                'id', 'title', 'severity', 'status',
                'bot__id', 'bot__name',
                'reported_by__id', 'reported_by__username', 'reported_by__email',
                'assigned_to__id', 'assigned_to__username', 'assigned_to__email',
                'created_at', 'updated_at',
            )
        )

        bugs = {
            "total": bugs_qs.count(),
            "total_open": bugs_agg['open'] + bugs_agg['in_progress'],
            "by_status": {
                "open":        bugs_agg['open'],
                "in_progress": bugs_agg['in_progress'],
                "resolved":    bugs_agg['resolved'],
                "closed":      bugs_agg['closed'],
            },
            "open_by_severity": {
                "critical": bugs_agg['critical'],
                "high":     bugs_agg['high'],
                "medium":   bugs_agg['medium'],
                "low":      bugs_agg['low'],
            },
            "by_bot": [
                {
                    "bot_id":      str(r['bot__id']) if r['bot__id'] else None,
                    "bot_name":    r['bot__name'] or "Unassigned",
                    "total":       r['total'],
                    "open":        r['open'],
                    "in_progress": r['in_progress'],
                    "resolved":    r['resolved'],
                    "critical":    r['critical'],
                    "high":        r['high'],
                }
                for r in bugs_by_bot
            ],
            "recent": [
                {
                    "id":                   str(r['id']),
                    "title":                r['title'],
                    "severity":             r['severity'],
                    "status":               r['status'],
                    "bot_id":               str(r['bot__id']) if r['bot__id'] else None,
                    "bot_name":             r['bot__name'],
                    "reported_by_id":       str(r['reported_by__id']),
                    "reported_by":          r['reported_by__username'],
                    "reported_by_email":    r['reported_by__email'],
                    "assigned_to_id":       str(r['assigned_to__id']) if r['assigned_to__id'] else None,
                    "assigned_to":          r['assigned_to__username'],
                    "assigned_to_email":    r['assigned_to__email'],
                    "created_at":           r['created_at'].isoformat(),
                    "updated_at":           r['updated_at'].isoformat(),
                }
                for r in recent_bugs
            ],
        }

        # ── Requests ─────────────────────────────────────────────────────────
        req_qs = Requests.objects.all() if is_super else Requests.objects.filter(
            Q(requested_by=user) | Q(assigned_to=user)
        )
        req_agg = req_qs.aggregate(
            pending=Count('id', filter=Q(status='pending')),
            approved=Count('id', filter=Q(status='approved')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            completed=Count('id', filter=Q(status='completed')),
            rejected=Count('id', filter=Q(status='rejected')),
        )
        requests_data = {"total": req_qs.count(), **req_agg}

        # ── Workflows ────────────────────────────────────────────────────────
        wf_qs = Workflow.objects.all() if is_super else Workflow.objects.filter(created_by=user)

        wf_agg = wf_qs.aggregate(
            saved=Count('id', filter=Q(status='saved')),
            queued=Count('id', filter=Q(status='queued')),
            running=Count('id', filter=Q(status='running')),
            completed=Count('id', filter=Q(status='completed')),
            failed=Count('id', filter=Q(status='failed')),
            total_actions=Sum('action_count'),
        )

        # Workflows per bot (with bot name + client/owner)
        wf_by_bot = (
            wf_qs
            .values(
                'bot__id',
                'bot__name',
                'bot__status',
                'bot__created_by__id',
                'bot__created_by__username',
                'bot__created_by__email',
            )
            .annotate(
                workflow_count=Count('id'),
                completed=Count('id', filter=Q(status='completed')),
                failed=Count('id', filter=Q(status='failed')),
                total_actions=Sum('action_count'),
            )
            .order_by('-workflow_count')
        )

        # Workflows per client (created_by user)
        wf_by_client = (
            wf_qs
            .values(
                'created_by__id',
                'created_by__username',
                'created_by__email',
            )
            .annotate(
                workflow_count=Count('id'),
                completed=Count('id', filter=Q(status='completed')),
                failed=Count('id', filter=Q(status='failed')),
                saved=Count('id', filter=Q(status='saved')),
                total_actions=Sum('action_count'),
            )
            .order_by('-workflow_count')
        )

        # Recent workflows with report status
        recent_workflows = list(
            wf_qs
            .select_related('bot', 'created_by', 'report')
            .order_by('-created_at')[:10]
            .values(
                'id',
                'workflow_name',
                'status',
                'action_count',
                'last_executed',
                'created_at',
                'bot__id',
                'bot__name',
                'created_by__id',
                'created_by__username',
                'created_by__email',
                'report__status',
                'report__execution_time',
                'report__executed_at',
            )
        )

        workflows = {
            "total": wf_qs.count(),
            "by_status": {
                "saved":     wf_agg['saved'],
                "queued":    wf_agg['queued'],
                "running":   wf_agg['running'],
                "completed": wf_agg['completed'],
                "failed":    wf_agg['failed'],
            },
            "total_actions_recorded": wf_agg['total_actions'] or 0,
            "by_bot": [
                {
                    "bot_id":       str(r['bot__id']) if r['bot__id'] else None,
                    "bot_name":     r['bot__name'] or "Unassigned",
                    "bot_status":   r['bot__status'],
                    "client_id":    str(r['bot__created_by__id']) if r['bot__created_by__id'] else None,
                    "client_name":  r['bot__created_by__username'],
                    "client_email": r['bot__created_by__email'],
                    "workflow_count":  r['workflow_count'],
                    "completed":       r['completed'],
                    "failed":          r['failed'],
                    "total_actions":   r['total_actions'] or 0,
                }
                for r in wf_by_bot
            ],
            "by_client": [
                {
                    "client_id":      str(r['created_by__id']),
                    "client_name":    r['created_by__username'],
                    "client_email":   r['created_by__email'],
                    "workflow_count": r['workflow_count'],
                    "completed":      r['completed'],
                    "failed":         r['failed'],
                    "saved":          r['saved'],
                    "total_actions":  r['total_actions'] or 0,
                }
                for r in wf_by_client
            ],
            "recent": [
                {
                    "id":             str(r['id']),
                    "name":           r['workflow_name'],
                    "status":         r['status'],
                    "action_count":   r['action_count'],
                    "last_executed":  r['last_executed'].isoformat() if r['last_executed'] else None,
                    "created_at":     r['created_at'].isoformat(),
                    "bot_id":         str(r['bot__id']) if r['bot__id'] else None,
                    "bot_name":       r['bot__name'],
                    "client_id":      str(r['created_by__id']),
                    "client_name":    r['created_by__username'],
                    "client_email":   r['created_by__email'],
                    "report_status":  r['report__status'],
                    "execution_time": r['report__execution_time'],
                    "report_executed_at": r['report__executed_at'].isoformat() if r['report__executed_at'] else None,
                }
                for r in recent_workflows
            ],
        }

        # ── Notifications ────────────────────────────────────────────────────
        # FIX: explicit isoformat() for datetime serialization
        notif_qs = Notification.objects.filter(user=user)
        recent_notifs = [
            {
                **n,
                "created_at": n["created_at"].isoformat() if n["created_at"] else None,
            }
            for n in notif_qs.order_by('-created_at')[:5].values(
                'id', 'title', 'message', 'notification_type', 'is_read', 'created_at'
            )
        ]
        notifications = {
            "unread_count": notif_qs.filter(is_read=False).count(),
            "recent": recent_notifs,
        }

        response = {
            "bots":          bots,
            "executions":    executions,
            "budget":        budget,
            "billing":       billing,
            "bugs":          bugs,
            "requests":      requests_data,
            "workflows":     workflows,
            "notifications": notifications,
        }
        if users_roles:
            response["users_roles"] = users_roles

        return Response(response)
