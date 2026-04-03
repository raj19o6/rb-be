from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from api.Bot.model import Bot
from api.BotAllotments.model import BotAllotments
from api.Executions.model import Executions
from api.Budget.model import Budget
from api.Billing.model import Billing
from api.Bugs.model import Bugs
from api.Requests.model import Requests
from api.Notification.model import Notification
from api.CustomRole.model import CustomRole


class GetDashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        is_super = user.is_superuser

        # --- Users & Roles (superuser only) ---
        users_roles = None
        if is_super:
            User = get_user_model()
            user_qs = User.objects.all()
            users_roles = {
                "users": {
                    "total": user_qs.count(),
                    "active": user_qs.filter(is_active=True).count(),
                    "inactive": user_qs.filter(is_active=False).count(),
                    "superusers": user_qs.filter(is_superuser=True).count(),
                },
                "roles": {
                    "system_roles": Group.objects.count(),
                    "custom_roles": CustomRole.objects.count(),
                    "total": Group.objects.count() + CustomRole.objects.count(),
                },
            }

        # --- Bots ---
        bot_qs = Bot.objects.all() if is_super else Bot.objects.filter(
            allotments__user=user
        )
        bots = {
            "total": bot_qs.count(),
            "active": bot_qs.filter(status='active').count(),
            "inactive": bot_qs.filter(status='inactive').count(),
            "maintenance": bot_qs.filter(status='maintenance').count(),
        }

        # --- Executions ---
        exec_qs = Executions.objects.all() if is_super else Executions.objects.filter(executed_by=user)
        exec_counts = {s: exec_qs.filter(status=s).count() for s in ['success', 'failed', 'running', 'queued', 'cancelled']}
        executions = {"total": exec_qs.count(), **exec_counts}

        # --- Budget ---
        budget_qs = Budget.objects.all() if is_super else Budget.objects.filter(user=user)
        budget_agg = budget_qs.aggregate(
            total_allocated=Sum('allocated_amount'),
            total_consumed=Sum('consumed_amount'),
        )
        budget = {
            "total_allocated": budget_agg['total_allocated'] or 0,
            "total_consumed": budget_agg['total_consumed'] or 0,
            "total_remaining": (budget_agg['total_allocated'] or 0) - (budget_agg['total_consumed'] or 0),
        }

        # --- Billing ---
        billing_qs = Billing.objects.all() if is_super else Billing.objects.filter(user=user)
        billing_agg = billing_qs.aggregate(total=Sum('amount'))
        billing = {
            "total_amount": billing_agg['total'] or 0,
            **{s: billing_qs.filter(status=s).aggregate(a=Sum('amount'))['a'] or 0 for s in ['paid', 'unpaid', 'overdue']},
        }

        # --- Bugs ---
        bugs_qs = Bugs.objects.filter(status__in=['open', 'in_progress']) if is_super else \
            Bugs.objects.filter(status__in=['open', 'in_progress']).filter(
                Q(reported_by=user) | Q(assigned_to=user)
            )
        open_bugs = {sev: bugs_qs.filter(severity=sev).count() for sev in ['low', 'medium', 'high', 'critical']}
        bugs = {"open": open_bugs, "total_open": bugs_qs.count()}

        # --- Requests ---
        req_qs = Requests.objects.all() if is_super else Requests.objects.filter(requested_by=user)
        req_counts = {s: req_qs.filter(status=s).count() for s in ['pending', 'approved', 'in_progress', 'completed', 'rejected']}
        requests_data = {"total": req_qs.count(), **req_counts}

        # --- Notifications (always scoped to current user) ---
        notif_qs = Notification.objects.filter(user=user)
        recent_notifs = notif_qs.order_by('-created_at')[:5].values(
            'id', 'title', 'message', 'notification_type', 'created_at'
        )
        notifications = {
            "unread_count": notif_qs.filter(is_read=False).count(),
            "recent": list(recent_notifs),
        }

        response = {
            "bots": bots,
            "executions": executions,
            "budget": budget,
            "billing": billing,
            "bugs": bugs,
            "requests": requests_data,
            "notifications": notifications,
        }
        if users_roles:
            response["users_roles"] = users_roles
        return Response(response)
