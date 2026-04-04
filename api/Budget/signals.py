from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender='api.Budget')
def track_budget_changes(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        previous = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    if previous.allocated_amount != instance.allocated_amount:
        from api.Budget.history_model import BudgetHistory
        BudgetHistory.objects.create(
            budget=previous,
            changed_by=instance.user,
            previous_allocated=previous.allocated_amount,
            new_allocated=instance.allocated_amount,
            note='Allocated amount updated via signal.',
        )
