from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='api.Payment')
def update_billing_on_payment(sender, instance, created, **kwargs):
    if instance.status == 'completed' and instance.billing.status != 'paid':
        from api.Billing.model import Billing
        Billing.objects.filter(pk=instance.billing_id).update(status='paid')
