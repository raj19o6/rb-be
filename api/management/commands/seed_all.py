from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Seed all records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']

        # existing
        call_command('seed_address', n)
        call_command('seed_test', n)

        # independent models
        call_command('seed_bot', n)
        call_command('seed_requests', n)
        call_command('seed_doc_category', n)
        call_command('seed_regex', n)
        call_command('seed_billing', n)
        call_command('seed_budget', n)
        call_command('seed_notification', n)
        call_command('seed_bugs', n)

        # FK-dependent models
        call_command('seed_bot_allotments', n)
        call_command('seed_bot_maintainance', n)
        call_command('seed_bot_prereq', n)
        call_command('seed_bot_functions', n)
        call_command('seed_credentials', n)
        call_command('seed_run_block_reasons', n)
        call_command('seed_doc_fields', n)
        call_command('seed_executions', n)

        self.stdout.write(self.style.SUCCESS(f'All seeds completed with count={n}'))
