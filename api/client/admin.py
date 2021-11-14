from django.contrib import admin
from client.models import WorklogWithInfo, IssuesInfo, FinologApiToken, FinologOrder, FinologProject


@admin.register(WorklogWithInfo)
class WorklogWithInfoAdmin(admin.ModelAdmin):
    pass


@admin.register(IssuesInfo)
class IssuesInfoAdmin(admin.ModelAdmin):
    list_display = ('key', 'agreed_order_key', )


@admin.register(FinologApiToken)
class FinologApiTokenAdmin(admin.ModelAdmin):
    pass


@admin.register(FinologOrder)
class FinologOrderAdmin(admin.ModelAdmin):
    list_display = ('jira_key', 'finolog_id',)


@admin.register(FinologProject)
class FinologProjectAdmin(admin.ModelAdmin):
    list_display = ('jira_key', 'finolog_id',)
