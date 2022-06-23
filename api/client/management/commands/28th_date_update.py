from django.core.management.base import BaseCommand
from datetime import datetime
from dateutil.relativedelta import *

from client.models import PeriodForDownloadModel


class Command(BaseCommand):
    """
    Updates the end date for downloading worklogs: takes the 28th of the current month and year.
    Also updates the number of days to download so that between the current date and the date of the previous update
    a month passed. For example, from 2022-04-28 to 2022-03-28 31 days should pass,
    and from 2022-03-28 to 2022-02-28 - 28.
    That is, the number of days is always different depending on the month.
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
