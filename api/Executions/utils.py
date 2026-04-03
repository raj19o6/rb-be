from django.utils import timezone


def mark_execution_running(execution):
    """Set status to running and record started_at timestamp."""
    execution.status = 'running'
    execution.started_at = timezone.now()
    execution.save(update_fields=['status', 'started_at'])


def mark_execution_success(execution):
    """Set status to success and record ended_at timestamp."""
    execution.status = 'success'
    execution.ended_at = timezone.now()
    execution.save(update_fields=['status', 'ended_at'])


def mark_execution_failed(execution, error_message=''):
    """Set status to failed, record ended_at, and update the execution report."""
    execution.status = 'failed'
    execution.ended_at = timezone.now()
    execution.save(update_fields=['status', 'ended_at'])

    from api.ExecutionReports.model import ExecutionReports
    ExecutionReports.objects.update_or_create(
        execution=execution,
        defaults={
            'summary': 'Execution failed.',
            'error_message': error_message,
        },
    )


def get_execution_duration(execution):
    """Return duration in seconds between started_at and ended_at, or None."""
    if execution.started_at and execution.ended_at:
        delta = execution.ended_at - execution.started_at
        return round(delta.total_seconds(), 2)
    return None


def get_executions_summary(user=None, bot=None):
    """
    Return a dict with counts per status.
    Optionally filter by user and/or bot.
    """
    from api.Executions.model import Executions
    from django.db.models import Count

    qs = Executions.objects.all()
    if user:
        qs = qs.filter(executed_by=user)
    if bot:
        qs = qs.filter(bot=bot)

    counts = qs.values('status').annotate(count=Count('id'))
    summary = {item['status']: item['count'] for item in counts}

    for status in ('queued', 'running', 'success', 'failed', 'cancelled'):
        summary.setdefault(status, 0)

    return summary
