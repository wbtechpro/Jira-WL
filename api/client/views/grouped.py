from rest_framework import serializers
from rest_framework.response import Response

from client.views.base import BaseWorklogListView
from client.models import FinologOrder, FinologProject


class WorklogSerializer(serializers.Serializer):
    # issue__agreed_order_key = serializers.CharField()
    issue__project = serializers.CharField()
    logged_time = serializers.IntegerField()
    issue__agreed_order_finolog__finolog_id = serializers.CharField()
    # issue__agreed_order_finolog__jira_key = serializers.CharField()

    def to_representation(self, instance):
        """
        Фишка в том, чтобы выделять только заказы из финолога.
        А для таких отдельно показывать и жира-ключ
        """
        grouped_worklog = super().to_representation(instance)

        # Вставляем жира ключи
        jira_key = ''
        if grouped_worklog['issue__agreed_order_finolog__finolog_id'] is not None \
                and grouped_worklog['issue__agreed_order_finolog__finolog_id'].isdigit():
            finolog_id = grouped_worklog['issue__agreed_order_finolog__finolog_id']
            jira_key = FinologOrder.objects.get(finolog_id=finolog_id).jira_key
        grouped_worklog['issue__agreed_order_finolog__jira_key'] = jira_key

        # Вставляем айдишники финолога
        finolog_project_id = FinologProject.objects.filter(jira_key=grouped_worklog['issue__project']).first()
        if finolog_project_id:
            finolog_project_id = int(finolog_project_id.finolog_id)
        else:
            finolog_project_id = 0

        grouped_worklog['issue__project_finolog_id'] = finolog_project_id

        category = FinologProject.objects.filter(jira_key=grouped_worklog['issue__project']).first()
        if category:
            if category.category_id.isdigit():
                grouped_worklog['issue__project__category_id'] = int(category.category_id)
        else:
            grouped_worklog['issue__project__category_id'] = 'Статья расходов не указана'

        return grouped_worklog


class GroupedByProjectWorklogView(BaseWorklogListView):

    serializer_class = WorklogSerializer

    def get_queryset(self):
        queryset = super().get_queryset().group_worklogs_by_agreed_orders()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        ret_dict = self._get_ret_dict(data)
        return Response(ret_dict)

    def _get_ret_dict(self, data):
        summed_hours = sum([i['logged_time'] for i in data])
        ret_dict = {
            'all_logged_seconds': summed_hours,
            'grouped_worklogs': data
        }
        return ret_dict


# Сериализатор и вью для группировки ворклогов по таскам Жиры

class WorklogIssueSerializer(serializers.Serializer):

    logged_time = serializers.IntegerField()
    issue__agreed_order_finolog__finolog_id = serializers.CharField()
    issue__key = serializers.CharField()
    issue__project = serializers.CharField()

    def to_representation(self, instance):
        """
        Отображает id заказа из Финолога, id таска из Жиры, проект и статью расходов (категорию)
        вне зависимости от того, сформирован ли в Финологе заказ на этот таск или нет
        """

        grouped_worklog = super().to_representation(instance)

        finolog_project_id = FinologProject.objects.filter(jira_key=grouped_worklog['issue__project']).first()
        if finolog_project_id:
            finolog_project_id = int(finolog_project_id.finolog_id)
        else:
            finolog_project_id = 0
        grouped_worklog['issue__project_finolog_id'] = finolog_project_id

        category = FinologProject.objects.filter(jira_key=grouped_worklog['issue__project']).first()
        if category:
            if category.category_id.isdigit():
                grouped_worklog['issue__project__category_id'] = int(category.category_id)
        else:
            grouped_worklog['issue__project__category_id'] = 'Статья расходов не указана'

        return grouped_worklog


class GroupedByIssueWorklogView(GroupedByProjectWorklogView):

    serializer_class = WorklogIssueSerializer

    def _get_ret_dict(self, data):
        summed_hours = sum([i['logged_time'] for i in data])
        ret_dict = {
            'all_logged_seconds': summed_hours,
            'grouped_worklogs': data
        }
        return ret_dict
