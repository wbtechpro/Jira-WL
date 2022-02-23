from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from client.jira_client import JiraClient
from client.helpers.helpers import get_unix_time_n_days_before_now
from client.models import WorklogWithInfo, IssuesInfo, FinologOrder, DaysForDownloadModel
from client.finolog import get_finolog_ids_for_all_jira_orders
from client.forms import period_in_days_does_not_exceed_3_months


class Command(BaseCommand):

    """
    Запускает Jira клиента.
    Удаляет все данные и записывает заново.
    """

    help = 'Запускает Jira клиента'

    def add_arguments(self, parser):
        parser.add_argument('days_before', nargs='?', type=int, default=None)

    def handle(self, *args, **options):

        with transaction.atomic():
            WorklogWithInfo.objects.all().delete()
            IssuesInfo.objects.all().delete()
            FinologOrder.objects.all().delete()

            days_before_from_admin = DaysForDownloadModel.objects.get(pk=1).days
            days_before_command_input = options['days_before']

            if days_before_from_admin is None and days_before_command_input is None:
                raise ValueError('Please enter the number of days for which you want to download worklogs in the '
                                 'admin panel or in the terminal. The command cannot be executed without the '
                                 'argument.')

            if days_before_command_input is not None:
                max_period = period_in_days_does_not_exceed_3_months()
                if days_before_command_input > max_period:
                    raise ValueError(
                        f'The number of days you entered exceeded the limit in the last three months. Please '
                        f'enter a number of days up to {max_period}.')

                prev_day_start = get_unix_time_n_days_before_now(days_before_command_input)

            elif days_before_command_input is None and days_before_from_admin is not None:
                prev_day_start = get_unix_time_n_days_before_now(days_before_from_admin)

            jira_client = JiraClient(settings.USERNAME, settings.API_TOKEN, since_timestamp=prev_day_start)
            jira_client.get_jira_data()

            jira_finolog_tuples = get_finolog_ids_for_all_jira_orders()
            FinologOrder.save_from_jira_finolog_tuples(jira_finolog_tuples)
