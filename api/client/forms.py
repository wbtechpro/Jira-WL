from django import forms
from dateutil.relativedelta import relativedelta


def period_in_days_does_not_exceed_3_months(end_date):
    """
    Проверяет, не превыашет ли количество заданных для загрузки ворклогов дней период в три предшествующих месяца от
    текущего месяца.
    """
    worklogs_download_perion_date = end_date - relativedelta(months=3)
    worklogs_download_perion_days = end_date - worklogs_download_perion_date
    return worklogs_download_perion_days.days


class WorklogsDownloadPeriodForm(forms.Form):
    end_date = forms.DateField(required=False, label='Конечная дата отсчета')
    period_in_days = forms.IntegerField(required=False, label='Количество дней')

    def clean_period_in_days(self):
        days = self.cleaned_data['period_in_days']
        end_date = self.cleaned_data['end_date']
        if days is not None and end_date is not None:
            if days > period_in_days_does_not_exceed_3_months(end_date):
                raise forms.ValidationError(f'Введенное вами количество дней превышает лимит в три месяца. '
                                            f'Пожалуйста, введите количеств'
                                            f'о дней, не превышающее {period_in_days_does_not_exceed_3_months(end_date)}.')
            return days
        else:
            return days
