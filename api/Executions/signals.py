from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal


@receiver(post_save, sender='api.Executions')
def handle_execution_created(sender, instance, created, **kwargs):
    """Only run legacy workflow-trigger check when execution was created
    manually via POST /executions/ (no request linked = old path).
    ExecuteWorkflowView already handles all checks before creating the record."""
    if created and instance.request is None:
        _check_and_trigger_workflow(instance)


@receiver(post_save, sender='api.Executions')
def handle_execution_success(sender, instance, created, **kwargs):
    if instance.status == 'success' and not created:
        _deduct_balance(instance)


def _check_and_trigger_workflow(execution):
    from api.BotAllotments.model import BotAllotments
    from api.Billing.model import Billing
    from api.Workflow.model import Workflow

    user = execution.executed_by
    bot  = execution.bot

    if not BotAllotments.objects.filter(user=user, bot=bot).exists():
        _fail_execution(execution, 'Bot is not allotted to you.')
        return

    billing = Billing.objects.filter(user=user, bot=bot, status='paid').first()
    if not billing:
        _fail_execution(execution, 'No paid billing found for this bot.')
        return

    workflow = Workflow.objects.filter(
        created_by=user, status='saved'
    ).order_by('-created_at').first()
    if not workflow:
        _fail_execution(execution, 'No saved workflow found to execute.')
        return

    cost = Decimal(str(workflow.action_count)) * billing.price_per_action
    if billing.balance_remaining < cost:
        _fail_execution(
            execution,
            f'Insufficient balance. Required: ₹{cost}, Available: ₹{billing.balance_remaining}'
        )
        return

    workflow.status = 'queued'
    workflow.save(update_fields=['status'])


def _deduct_balance(execution):
    from api.Billing.model import Billing
    from api.Workflow.model import Workflow

    billing = Billing.objects.filter(
        user=execution.executed_by,
        bot=execution.bot,
        status='paid'
    ).first()
    if not billing:
        return

    workflow = Workflow.objects.filter(
        metadata__execution_id=str(execution.id)
    ).first() or Workflow.objects.filter(
        created_by=execution.executed_by,
        status='completed'
    ).order_by('-updated_at').first()

    if not workflow:
        return

    cost = Decimal(str(workflow.action_count)) * billing.price_per_action
    billing.balance_remaining = max(Decimal('0'), billing.balance_remaining - cost)
    billing.save(update_fields=['balance_remaining'])


def _fail_execution(execution, reason):
    from api.Executions.model import Executions
    Executions.objects.filter(pk=execution.pk).update(
        status='cancelled',
        failure_reason=reason,
        ended_at=timezone.now(),
    )
