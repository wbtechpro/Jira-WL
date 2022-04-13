from django.core.management.base import BaseCommand
from datetime import datetime
from dateutil.relativedelta import *

from client.models import PeriodForDownloadModel


class Command(BaseCommand):
    """
    Обновляет конечную дату для промежуточного (раз в неделю ночью с понедельника на вторник) скачивания ворклогов:
    прибавляет неделю к дате предыдущего вторника. Так, если дата предыдущего вторника - 2022-04-12,
    то дата следующего - 2022-04-19.
    Количество дней для скачивания ворклогов - 90. Его можно будет в любой момент поменять в админке
    """

    def handle(self, *args, **options):
        today = datetime.today()
        day_of_week = today.weekday()
        if day_of_week == 1 and today.day != 28:
            next_tuesday = today + relativedelta(weeks=1)
        else:
            return None
        model_instance = PeriodForDownloadModel.objects.get(pk=1)
        model_instance.end_date = next_tuesday
        model_instance.days = 90
        model_instance.save()
