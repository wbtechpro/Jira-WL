from django import forms
from datetime import date
from dateutil.relativedelta import relativedelta


def period_in_days_does_not_exceed_3_months():
    """
    Проверяет, не превыашет ли количество заданных для загрузки ворклогов дней период в три предшествующих месяца от
    текущего месяца. Временной диапазон рассчитывается не от текущего числа месяца, а от первого. То есть, к примеру,
    если сегодня 18.02.2022, то ворклоги будут отображаться за период с 01.02.2022 по 01.11.2021
    """
    first_day_of_month = date.today() - relativedelta(days=date.today().day - 1)
    worklogs_download_perion_date = first_day_of_month - relativedelta(months=3)
    worklogs_download_perion_days = first_day_of_month - worklogs_download_perion_date
    return worklogs_download_perion_days.days


class WorklogsDownloadPeriodForm(forms.Form):
    period_in_days = forms.IntegerField(required=False, label='Количество дней')

    def clean_period_in_days(self):
        days = self.cleaned_data['period_in_days']
        if days > period_in_days_does_not_exceed_3_months():
            raise forms.ValidationError(f'Введенное вами количество дней превышает лимит в последние три месяца. '
                                        f'Пожалуйста, введите количеств'
                                        f'о дней, не превышающее {period_in_days_does_not_exceed_3_months()}.')
        return days
