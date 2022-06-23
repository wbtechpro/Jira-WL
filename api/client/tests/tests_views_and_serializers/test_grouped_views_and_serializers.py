from django.db.models import Sum

from .test_views_and_serializers_setup import ViewsAndSerializersTestSetUp
from client.models import WorklogWithInfo


class GroupedByProjectWorklogsViewAndSerializer(ViewsAndSerializersTestSetUp):

    def test_grouped_by_projects_view_and_serializer_get(self):
        """
        Checks the operation of the view and serializer, which return information about specific projects,
        orders and the time spent on them, as well as the total time spent on all projects and orders, with the get
        method The serializer also adds the project key (jira_key) in case the order has been matched
        """
        response = self.client.get(self.grouped_by_projects_worklogs_view)

        self.assertEqual(response.status_code, 200)
        # Checking the display of information about the time spent on all projects and orders (def _get_ret_dict)
        self.assertEqual(response.data['all_logged_seconds'], WorklogWithInfo.objects.aggregate(
            Sum('time_spent_seconds'))['time_spent_seconds__sum'])
        self.assertEqual(len(response.data['grouped_worklogs']), 3)

        # Checking a worklog that does not have a project specified and for which there is no order in Finolog (data
        # only in the WorklogWithInfo database)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__project'], None)
        self.assertEqual(response.data['grouped_worklogs'][0]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__agreed_order_finolog__finolog_id'], None)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__agreed_order_finolog__jira_key'], "")
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__project_finolog_id'], 0)

        # Checking a worklog that has a project and an order in Finolog (data in the database WorklogWithInfo,
        # IssuesInfo, FinologOrder, FinologProject)
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__project'], 'add_test')
        self.assertEqual(response.data['grouped_worklogs'][1]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__agreed_order_finolog__finolog_id'], '3')
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__agreed_order_finolog__jira_key'], 'TEST-234')
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__project_finolog_id'], 3)

        # Checking a worklog that has a project, but there is no information about the order in Finolog (data in the
        # database WorklogWithInfo, IssuesInfo)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__project'], 'test')
        self.assertEqual(response.data['grouped_worklogs'][2]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__agreed_order_finolog__finolog_id'], None)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__agreed_order_finolog__jira_key'], "")
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__project_finolog_id'], 0)

    def test_grouped_by_projects_view_and_serializer_head(self):
        """
        Checks the operation of the view and the serializer, which return information about specific projects,
        orders and the time spent on them, as well as the total time spent on all projects and orders, with the head
        method
        """
        response = self.client.head(self.grouped_by_projects_worklogs_view)
        self.assertEqual(response.status_code, 200)
        # Checking the display of information about the time spent on all projects and orders (def _get_ret_dict)
        self.assertEqual(response.data['all_logged_seconds'], WorklogWithInfo.objects.aggregate(
        Sum('time_spent_seconds'))['time_spent_seconds__sum'])
        self.assertEqual(len(response.data['grouped_worklogs']), 3)

        # Checking a worklog that does not have a project specified and for which there is no order in Finolog (data
        # only in the WorklogWithInfo database)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__project'], None)
        self.assertEqual(response.data['grouped_worklogs'][0]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__agreed_order_finolog__finolog_id'], None)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__agreed_order_finolog__jira_key'], "")
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__project_finolog_id'], 0)

        # Checking a worklog that has a project and an order in Finolog (data in the database WorklogWithInfo,
        # IssuesInfo, FinologOrder, FinologProject)
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__project'], 'add_test')
        self.assertEqual(response.data['grouped_worklogs'][1]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__agreed_order_finolog__finolog_id'], '3')
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__agreed_order_finolog__jira_key'], 'TEST-234')
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__project_finolog_id'], 3)

        # Checking a worklog that has a project, but there is no information about the order in Finolog (data in the
        # database WorklogWithInfo, IssuesInfo)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__project'], 'test')
        self.assertEqual(response.data['grouped_worklogs'][2]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__agreed_order_finolog__finolog_id'], None)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__agreed_order_finolog__jira_key'], "")
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__project_finolog_id'], 0)

    def test_grouped_by_projects_view_and_serializer_prohibited_methods(self):
        """
        Checks that the view does not work with http methods other than those specified (get, head)
        """
        response = self.client.post(self.grouped_by_projects_worklogs_view)
        self.assertEqual(response.status_code, 405)

    # COMMENT ON PAGINATION OF PROJECT-GROUPED WORKLOGS

    # Despite the fact that the code (views.grouped.py, class GroupedByProjectWorklogView, func. list) provides
    # pagination, the page size is not set in the project. According to the documentation, in such cases, the settings
    # are considered set to None ("Both DEFAULT_PAGINATION_CLASS and PAGE_SIZE are None by default"), which means
    # pagination in the project does not work ("Pagination can be turned off by setting the pagination class to None").
    # Accordingly, this part of the code is not covered by tests


class GroupedByIssuesWorklogsViewAndSerializer(ViewsAndSerializersTestSetUp):

    def test_grouped_by_issues_view_and_serializer_get(self):
        """
        Checks the operation of the view and the serializer, which return information about specific tasks,
        orders and the time spent on them, as well as the total time spent on all tasks and orders, with the get method
        """
        response = self.client.get(self.grouped_by_issues_worklogs_view)
        self.assertEqual(response.status_code, 200)

        # Checking the display of information about the time spent on all tasks and orders (def _get_ret_dict)
        self.assertEqual(response.data['all_logged_seconds'], WorklogWithInfo.objects.aggregate(
            Sum('time_spent_seconds'))['time_spent_seconds__sum'])
        self.assertEqual(len(response.data['grouped_worklogs']), 3)

        # Checking a worklog that does not have a task and for which there is no order in Finolog (data only in the
        # WorklogWithInfo database)
        self.assertEqual(response.data['grouped_worklogs'][0]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__agreed_order_finolog__finolog_id'], None)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__key'], None)

        # Checking a worklog that has a task and an order in Finolog (data in the database WorklogWithInfo, IssuesInfo,
        # FinologOrder)
        self.assertEqual(response.data['grouped_worklogs'][1]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__agreed_order_finolog__finolog_id'], '3')
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__key'], 'add_test-234')

        # Checking a worklog that has a task, but there is no information about the order in Finolog (data in the
        # database WorklogWithInfo, IssuesInfo)
        self.assertEqual(response.data['grouped_worklogs'][2]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__agreed_order_finolog__finolog_id'], None)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__key'], 'test-123')

    def test_grouped_by_issues_view_and_serializer_head(self):
        """
        Checks the operation of the view and the serializer, which return information about specific projects,
        orders and the time spent on them, as well as the total time spent on all projects and orders, with the head
        method
        """
        response = self.client.head(self.grouped_by_issues_worklogs_view)
        self.assertEqual(response.status_code, 200)

        # Checking the display of information about the time spent on all tasks and orders (def _get_ret_dict)
        self.assertEqual(response.data['all_logged_seconds'], WorklogWithInfo.objects.aggregate(
            Sum('time_spent_seconds'))['time_spent_seconds__sum'])
        self.assertEqual(len(response.data['grouped_worklogs']), 3)

        # Checking a worklog that does not have a task and for which there is no order in Finolog (data only in the
        # WorklogWithInfo database)
        self.assertEqual(response.data['grouped_worklogs'][0]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__agreed_order_finolog__finolog_id'],
                         None)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__key'], None)

        # Checking a worklog that has a task and an order in Finolog (data in the database WorklogWithInfo, IssuesInfo,
        # FinologOrder)
        self.assertEqual(response.data['grouped_worklogs'][1]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__agreed_order_finolog__finolog_id'], '3')
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__key'], 'add_test-234')

        # Checking a worklog that has a task, but there is no information about the order in Finolog (data in the
        # database WorklogWithInfo, IssuesInfo)
        self.assertEqual(response.data['grouped_worklogs'][2]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__agreed_order_finolog__finolog_id'],
                         None)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__key'], 'test-123')

    def test_grouped_by_issues_view_and_serializer_prohibited_methods(self):
        """
        Checks that the view does not work with http methods other than those specified (get, head)
        """
        response = self.client.post(self.grouped_by_issues_worklogs_view)
        self.assertEqual(response.status_code, 405)
