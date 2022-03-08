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
    Запускает Jira клиента.
    Удаляет все данные и записывает заново.
    """

    help = 'Запускает Jira клиента'

    # Для того, чтобы передать аргументы команде run_client вручную, необходимо указать --start-date и/или --days_before
    # соответствнно. Это сделано для того, чтобы аргументы не были позиционными и чтобы можно было комбинировать
    # значения, введенные вручную, со значениями из админки
    def add_arguments(self, parser):
        parser.add_argument('--start_date', nargs='?', type=str, default=None)  # дату необходимо вводить в формате YYYY-MM-DD
        parser.add_argument('--days_before', nargs='?', type=int, default=None)

    def handle(self, *args, **options):

        with transaction.atomic():
            WorklogWithInfo.objects.all().delete()
            IssuesInfo.objects.all().delete()
            FinologOrder.objects.all().delete()

            days_before_from_admin = PeriodForDownloadModel.objects.get(pk=1).days
            start_date_from_admin = PeriodForDownloadModel.objects.get(pk=1).start_date
            days_before_command_input = options['days_before']
            start_date = options['start_date']  # стартовая дата, вручную переданная команде run_client как аргумент

            if start_date is None:  # проверка, что считать стартовой датой отсчета
                if start_date_from_admin is None:
                    start_date = datetime.datetime.now()  # дефолтное значение стартовой даты - текущая дата
                else:
                    start_date = start_date_from_admin
            else:
                try:
                    datetime.datetime.strptime(start_date, '%Y-%m-%d')
                except ValueError:
                    raise ValueError('Incorrect date format, should be YYYY-MM-DD')
                else:
                    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()

            if days_before_from_admin is None and days_before_command_input is None:
                raise ValueError('Please enter the number of days for which you want to download worklogs in the '
                                 'admin panel or in the terminal. The command cannot be executed without the '
                                 'argument.')

            if days_before_command_input is not None:
                max_period = period_in_days_does_not_exceed_3_months(start_date)
                if days_before_command_input > max_period:
                    raise ValueError(
                        f'The number of days you entered exceeded the limit in the last three months. Please '
                        f'enter a number of days up to {max_period}.')

                end_date = get_unix_time_n_days_before_date(days_before_command_input, start_date)[0]
                start_date = get_unix_time_n_days_before_date(days_before_command_input, start_date)[1]

            elif days_before_command_input is None and days_before_from_admin is not None:
                end_date = get_unix_time_n_days_before_date(days_before_from_admin, start_date)[0]
                start_date = get_unix_time_n_days_before_date(days_before_from_admin, start_date)[1]

            jira_client = JiraClient(settings.USERNAME, settings.API_TOKEN, end_date=end_date, start_date=start_date)
            jira_client.get_jira_data()

            jira_finolog_tuples = get_finolog_ids_for_all_jira_orders()
            FinologOrder.save_from_jira_finolog_tuples(jira_finolog_tuples)
