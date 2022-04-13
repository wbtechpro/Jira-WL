from django.core.management.base import BaseCommand
from datetime import datetime
from dateutil.relativedelta import *

from client.models import PeriodForDownloadModel


class Command(BaseCommand):
    """
    Обновляет конечную дату для скачивания ворклогов: берет 28 число текущих месяца и года.
    Также обновляет количество дней для скачивания так, чтобы между текущей датой и датой предыдущего обновления
    проходил месяц. К примеру, с 2022-04-28 до 2022-03-28 должен пройти 31 день, а с 2022-03-28 до 2022-02-28 - 28.
    То есть количество дней всегда разное в зависимости от месяца
    """

    def handle(self, *args, **options):
        current_date_for_worklogs = datetime.today()
        if current_date_for_worklogs.day == 28:
            previous_date_for_worklogs = current_date_for_worklogs - relativedelta(months=1)
            days_to_get_updated_date = abs(current_date_for_worklogs - previous_date_for_worklogs).days

            model_instance = PeriodForDownloadModel.objects.get(pk=1)
            model_instance.end_date = current_date_for_worklogs
            model_instance.days = days_to_get_updated_date
            model_instance.save()
        else:
            return
