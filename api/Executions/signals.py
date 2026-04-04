from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal


@receiver(post_save, sender='api.Executions')
def handle_execution_created(sender, instance, created, **kwargs):
    if created:
        _check_and_trigger_workflow(instance)


@receiver(post_save, sender='api.Executions')
def handle_execution_completion(sender, instance, created, **kwargs):
    if instance.status in ('success', 'failed') and not created:
        from api.ExecutionReports.model import ExecutionReports
        ExecutionReports.objects.get_or_create(
            execution=instance,
            defaults={
                'summary': f'Execution {instance.status}.',
                'logs': '',
                'error_message': '' if instance.status == 'success' else 'Execution failed.',
            }
        )

    if instance.status == 'success' and not created:
        _deduct_balance(instance)


def _check_and_trigger_workflow(execution):
    from api.BotAllotments.model import BotAllotments
    from api.Billing.model import Billing
    from api.Workflow.model import Workflow

    user = execution.executed_by
    bot = execution.bot

    # 1. Check bot is allotted to this client
    if not BotAllotments.objects.filter(user=user, bot=bot).exists():
        _fail_execution(execution, 'Bot is not allotted to you.')
        return

    # 2. Check client has a paid billing for this bot
    billing = Billing.objects.filter(user=user, bot=bot, status='paid').first()
    if not billing:
        _fail_execution(execution, 'No paid billing found for this bot.')
        return

    # 3. Get latest saved workflow to know action_count
    workflow = Workflow.objects.filter(
        created_by=user, status='saved'
    ).order_by('-created_at').first()

    if not workflow:
        _fail_execution(execution, 'No saved workflow found to execute.')
        return

    # 4. Check if balance covers the cost of this workflow run
    cost = Decimal(str(workflow.action_count)) * billing.price_per_action
    if billing.balance_remaining < cost:
        _fail_execution(
            execution,
            f'Insufficient balance. Required: ₹{cost}, Available: ₹{billing.balance_remaining}'
        )
        return

    # All checks passed — queue the workflow
    workflow.status = 'queued'
    workflow.save(update_fields=['status'])  # triggers Workflow signal → Jenkins


def _deduct_balance(execution):
    """Deduct action cost from billing balance after successful execution"""
    from api.Billing.model import Billing
    from api.Workflow.model import Workflow
    from django.db.models import F

    billing = Billing.objects.filter(
        user=execution.executed_by,
        bot=execution.bot,
        status='paid'
    ).first()

    if not billing:
        return

    # Get the workflow that was just executed
    workflow = Workflow.objects.filter(
        created_by=execution.executed_by,
        status__in=['queued', 'running', 'completed']
    ).order_by('-updated_at').first()

    if not workflow:
        return

    cost = Decimal(str(workflow.action_count)) * billing.price_per_action
    billing.balance_remaining = max(Decimal('0'), billing.balance_remaining - cost)
    billing.save(update_fields=['balance_remaining'])


def _fail_execution(execution, reason):
    from api.Executions.model import Executions
    from api.ExecutionReports.model import ExecutionReports
    Executions.objects.filter(pk=execution.pk).update(
        status='cancelled',
        ended_at=timezone.now()
    )
    execution.refresh_from_db()
    ExecutionReports.objects.get_or_create(
        execution=execution,
        defaults={
            'summary': 'Execution blocked.',
            'logs': '',
            'error_message': reason,
        }
    )
