from django.db.models.signals import post_save
from django.dispatch import receiver


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
        from api.Budget.model import Budget
        from django.db.models import F
        Budget.objects.filter(
            user=instance.executed_by,
            bot=instance.bot,
        ).update(consumed_amount=F('consumed_amount') + 1)
