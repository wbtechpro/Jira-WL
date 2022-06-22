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
        The point is to highlight only orders from Finolog.
        And for such separately show Jira key
        """
        grouped_worklog = super().to_representation(instance)

        # Insert Jira keys
        jira_key = ''
        if grouped_worklog['issue__agreed_order_finolog__finolog_id'] is not None \
                and grouped_worklog['issue__agreed_order_finolog__finolog_id'].isdigit():
            finolog_id = grouped_worklog['issue__agreed_order_finolog__finolog_id']
            jira_key = FinologOrder.objects.get(finolog_id=finolog_id).jira_key
        grouped_worklog['issue__agreed_order_finolog__jira_key'] = jira_key

        # Insert Finolog ids
        finolog_project_id = FinologProject.objects.filter(jira_key=grouped_worklog['issue__project']).first()
        if finolog_project_id:
            finolog_project_id = int(finolog_project_id.finolog_id)
        else:
            finolog_project_id = 0

        grouped_worklog['issue__project_finolog_id'] = finolog_project_id

        category = FinologProject.objects.filter(jira_key=grouped_worklog['issue__project']).first()
        if category:
            if category.category_id.isdigit():
               category = category.category_id
            else:
               category = 'Статья расходов не указана'
        else:
            category = 'Статья расходов не указана'

        grouped_worklog['issue__project_category_id'] = category

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


# Serializer and view for grouping worklogs by Jira tasks

class WorklogIssueSerializer(serializers.Serializer):

    logged_time = serializers.IntegerField()
    issue__agreed_order_finolog__finolog_id = serializers.CharField()
    issue__key = serializers.CharField()
    issue__project = serializers.CharField()

    def to_representation(self, instance):
        """
        Displays order id from Finolog, task id from Jira, project and expense item (category), regardless of
        whether the order for this task is generated in Finolog or not
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
                category = category.category_id
            else:
                category = 'Статья расходов не указана'
        else:
            category = 'Статья расходов не указана'

        grouped_worklog['issue__project_category_id'] = category

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
