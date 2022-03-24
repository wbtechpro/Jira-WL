from django.contrib import admin, messages
from django.shortcuts import render
from django.urls import path

from client.models import WorklogWithInfo, IssuesInfo, FinologApiToken, FinologOrder, FinologProject,\
    PeriodForDownloadModel
from client.forms import WorklogsDownloadPeriodForm


@admin.register(WorklogWithInfo)
class WorklogWithInfoAdmin(admin.ModelAdmin):
    pass


@admin.register(IssuesInfo)
class IssuesInfoAdmin(admin.ModelAdmin):
    list_display = ('key', 'agreed_order_key',)


@admin.register(FinologApiToken)
class FinologApiTokenAdmin(admin.ModelAdmin):
    pass


@admin.register(FinologOrder)
class FinologOrderAdmin(admin.ModelAdmin):
    list_display = ('jira_key', 'finolog_id',)


@admin.register(FinologProject)
class FinologProjectAdmin(admin.ModelAdmin):
    list_display = ('jira_key', 'finolog_id',)


# ДОБАВЛЕНИЕ В АДМИН-ПАНЕЛЬ ВОЗМОЖНОСТИ УКАЗАНИЯ КОЛИЧЕСТВА ДНЕЙ, ЗА КОТОРОЕ НЕОБХОДИМО ЗАГРУЗИТЬ ВОРКЛОГИ,
# И КОНЕЧНОЙ ДАТЫ ОТСЧЕТА

class WorklogsDownloadPeriodAdmin(admin.ModelAdmin):
    model = PeriodForDownloadModel

    def post_download_period_in_days_via_admin(self, request):
        try:
            days_for_template = PeriodForDownloadModel.objects.get(pk=1).days
        except PeriodForDownloadModel.DoesNotExist:
            days_for_template = None

        try:
            end_date_for_template = PeriodForDownloadModel.objects.get(pk=1).end_date
        except PeriodForDownloadModel.DoesNotExist:
            end_date_for_template = None

        if request.method == 'POST':
            form = WorklogsDownloadPeriodForm(request.POST, initial={'period_in_days': days_for_template,
                                                                     'end_date': end_date_for_template})
            if form.is_valid():
                days, created = PeriodForDownloadModel.objects.update_or_create(
                    pk=1, defaults={'days': form.cleaned_data['period_in_days']})
                end_date, created = PeriodForDownloadModel.objects.update_or_create(
                    pk=1, defaults={'end_date': form.cleaned_data['end_date']})
                messages.success(request, 'Form submission successful')
        else:
            form = WorklogsDownloadPeriodForm(initial={'period_in_days': days_for_template,
                                                       'end_date': end_date_for_template})

        return render(request, 'admin/custom_admin_template.html', {'form': form})

    def get_urls(self):
        view_name = f'{self.model._meta.app_label}_{self.model._meta.model_name}_changelist'
        return [
            path('worklogs-download-period/', self.post_download_period_in_days_via_admin, name=view_name),
        ]


admin.site.register(PeriodForDownloadModel, WorklogsDownloadPeriodAdmin)
