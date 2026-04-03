from django.core.exceptions import ValidationError


def validate_positive_amount(value):
    if value <= 0:
        raise ValidationError('Amount must be greater than zero.')


def validate_transaction_id(value):
    if not value or len(value.strip()) < 5:
        raise ValidationError('Transaction ID must be at least 5 characters.')
