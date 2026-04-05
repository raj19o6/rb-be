from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from api.Workflow.model import Workflow
from api.Billing.model import Billing


class GetTotalPriceForExecution(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        # Total cost = sum of (execution_count * action_count * price_per_action) per workflow
        # We join Workflow with Billing on (created_by, bot)
        target_user_id = user_id or str(request.user.id)

        workflows = Workflow.objects.filter(
            created_by_id=target_user_id,
            execution_count__gt=0,
        ).select_related('bot')

        total_cost = 0
        breakdown  = []

        for wf in workflows:
            billing = Billing.objects.filter(
                user_id=target_user_id, bot=wf.bot, status='paid'
            ).first()
            price_per_action = billing.price_per_action if billing else 0
            cost = wf.total_actions_consumed * float(price_per_action)
            total_cost += cost
            breakdown.append({
                'workflow_id':            str(wf.id),
                'workflow_name':          wf.workflow_name,
                'action_count':           wf.action_count,
                'execution_count':        wf.execution_count,
                'total_actions_consumed': wf.total_actions_consumed,
                'price_per_action':       str(price_per_action),
                'total_cost':             round(cost, 2),
            })

        return Response({
            'user_id':    target_user_id,
            'total_price': round(total_cost, 2),
            'breakdown':  breakdown,
        })
