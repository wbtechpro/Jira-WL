import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from client.jira_client import JiraClient
from client.helpers.helpers import get_unix_time_n_days_before_date
from client.models import WorklogWithInfo, IssuesInfo, FinologOrder, PeriodForDownloadModel
from client.finolog import get_finolog_ids_for_all_jira_orders
from client.forms import period_in_days_does_not_exceed_3_months


class Command(BaseCommand):
    """
    Launches the Jira client.
    Deletes all data and writes again.
    """

    help = 'Запускает Jira клиента'

    # In order to manually pass arguments to the run_client command, --end-date and/or --days_before must be specified,
    # respectively. This is done so that the arguments are not positional and so that you can combine manually entered
    # values with values from the admin panel
    def add_arguments(self, parser):
        parser.add_argument('--end_date', nargs='?', type=str, default=None)  # date must be entered in YYYY-MM-DD format
        parser.add_argument('--days_before', nargs='?', type=int, default=None)

    def handle(self, *args, **options):

        with transaction.atomic():
            WorklogWithInfo.objects.all().delete()
            IssuesInfo.objects.all().delete()
            FinologOrder.objects.all().delete()

            days_before_from_admin = PeriodForDownloadModel.objects.get(pk=1).days
            end_date_from_admin = PeriodForDownloadModel.objects.get(pk=1).end_date
            days_before_command_input = options['days_before']
            end_date = options['end_date']  # the end date manually passed to the run_client command as an argument

            if end_date is None:  # checking what is considered the end date of the countdown
                if end_date_from_admin is None:
                    end_date = datetime.datetime.now()  # the default value of the end date is the current date
                else:
                    end_date = end_date_from_admin
            else:
                try:
                    datetime.datetime.strptime(end_date, '%Y-%m-%d')
                except ValueError:
                    raise ValueError('Incorrect date format, should be YYYY-MM-DD')
                else:
                    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

            if days_before_from_admin is None and days_before_command_input is None:
                raise ValueError('Please enter the number of days for which you want to download worklogs in the '
                                 'admin panel or in the terminal. The command cannot be executed without the '
                                 'argument.')

            if days_before_command_input is not None:
                max_period = period_in_days_does_not_exceed_3_months(end_date)
                if days_before_command_input > max_period:
                    raise ValueError(
                        f'The number of days you entered exceeded the limit in the last three months. Please '
                        f'enter a number of days up to {max_period}.')

                start_date = get_unix_time_n_days_before_date(days_before_command_input, end_date)[0]
                end_date = get_unix_time_n_days_before_date(days_before_command_input, end_date)[1]

            elif days_before_command_input is None and days_before_from_admin is not None:
                start_date = get_unix_time_n_days_before_date(days_before_from_admin, end_date)[0]
                end_date = get_unix_time_n_days_before_date(days_before_from_admin, end_date)[1]

            jira_client = JiraClient(settings.USERNAME, settings.API_TOKEN, start_date=start_date, end_date=end_date)
            jira_client.get_jira_data()

            jira_finolog_tuples = get_finolog_ids_for_all_jira_orders()
            FinologOrder.save_from_jira_finolog_tuples(jira_finolog_tuples)
