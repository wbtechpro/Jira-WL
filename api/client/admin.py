from django.contrib import admin
from django.shortcuts import render
from django.urls import path

from client.models import WorklogWithInfo, IssuesInfo, FinologApiToken, FinologOrder, FinologProject, ProxyModel
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


# ДОБАВЛЕНИЕ В АДМИН-ПАНЕЛЬ ВОЗМОЖНОСТИ УКАЗАНИЯ КОЛИЧЕСТВА ДНЕЙ, ЗА КОТОРОЕ НЕОБХОДИМО ЗАГРУЗИТЬ ВОРКЛОГИ

class WorklogsDownloadPeriodAdmin(admin.ModelAdmin):
    model = ProxyModel

    def post_download_period_in_days_via_admin(self, request):
        if request.method == 'POST':
            form = WorklogsDownloadPeriodForm(request.POST)
            if form.is_valid():
                days_from_admin = form.cleaned_data['period_in_days']
        else:
            form = WorklogsDownloadPeriodForm()

        return render(request, 'admin/custom_admin_template.html', {'form': form})

    def get_urls(self):
        view_name = f'{self.model._meta.app_label}_{self.model._meta.model_name}_changelist'
        return [
            path('worklogs-download-period/', self.post_download_period_in_days_via_admin, name=view_name),
        ]


admin.site.register(ProxyModel, WorklogsDownloadPeriodAdmin)
