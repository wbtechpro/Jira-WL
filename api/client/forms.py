from django import forms
from dateutil.relativedelta import relativedelta


def period_in_days_does_not_exceed_3_months(start_date):
    """
    Проверяет, не превыашет ли количество заданных для загрузки ворклогов дней период в три предшествующих месяца от
    текущего месяца.
    """
    worklogs_download_perion_date = start_date - relativedelta(months=3)
    worklogs_download_perion_days = start_date - worklogs_download_perion_date
    return worklogs_download_perion_days.days


class WorklogsDownloadPeriodForm(forms.Form):
    start_date = forms.DateField(required=False, label='Стартовая дата отсчета')
    period_in_days = forms.IntegerField(required=False, label='Количество дней')

    def clean_period_in_days(self):
        days = self.cleaned_data['period_in_days']
        start_date = self.cleaned_data['start_date']
        if days is not None and start_date is not None:
            if days > period_in_days_does_not_exceed_3_months(start_date):
                raise forms.ValidationError(f'Введенное вами количество дней превышает лимит в три месяца. '
                                            f'Пожалуйста, введите количеств'
                                            f'о дней, не превышающее {period_in_days_does_not_exceed_3_months(start_date)}.')
            return days
        else:
            return days
