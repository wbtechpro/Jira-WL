from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from client.jira_client import JiraClient
from client.helpers.helpers import get_unix_time_n_days_before_now
from client.models import WorklogWithInfo, IssuesInfo, FinologOrder
from client.finolog import get_finolog_ids_for_all_jira_orders


class Command(BaseCommand):

    """
    Запускает Jira клиента.
    Удаляет все данные и записывает заново.
    """

    help = 'Запускает Jira клиента'

    def add_arguments(self, parser):
        parser.add_argument('days_before', nargs='+', type=int)

    def handle(self, *args, **options):

        with transaction.atomic():
            WorklogWithInfo.objects.all().delete()
            IssuesInfo.objects.all().delete()
            FinologOrder.objects.all().delete()

            prev_day_start = get_unix_time_n_days_before_now(options['days_before'][0])
            jira_client = JiraClient(settings.USERNAME, settings.API_TOKEN, since_timestamp=prev_day_start)
            jira_client.get_jira_data()

            jira_finolog_tuples = get_finolog_ids_for_all_jira_orders()
            FinologOrder.save_from_jira_finolog_tuples(jira_finolog_tuples)
