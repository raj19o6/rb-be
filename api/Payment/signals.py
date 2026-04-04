from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F


@receiver(post_save, sender='api.Payment')
def update_billing_on_payment(sender, instance, created, **kwargs):
    if instance.status == 'completed':
        from api.Billing.model import Billing
        billing = Billing.objects.filter(pk=instance.billing_id).first()
        if not billing:
            return
        update_fields = {'balance_remaining': F('balance_remaining') + instance.amount}
        if billing.status != 'paid':
            update_fields['status'] = 'paid'
        Billing.objects.filter(pk=instance.billing_id).update(**update_fields)
