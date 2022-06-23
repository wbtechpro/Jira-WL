from collections import OrderedDict

from .test_views_and_serializers_setup import ViewsAndSerializersTestSetUp
from client.models import FinologProject


class GroupedByProjectWorklogsViewAndSerializer(ViewsAndSerializersTestSetUp):

    def test_finolog_projects_view_and_serializer_display_get(self):
        """
        Checks the operation of the list view function and the serializer, which display data on projects agreed as an order in Finolog, from the FinologProject database, with the get method
        One project added for tests in the database
        """
        response = self.client.get(self.finolog_projects_view)
        finolog_projects__info = FinologProject.objects.values()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(finolog_projects__info))
        self.assertEqual(response.data[0], OrderedDict(list((x, y) for x, y in finolog_projects__info[0].items())))

    def test_finolog_projects_view_and_serializer_display_head(self):
        """
        Checks the operation of the list view function and the serializer, which display data on projects agreed as
        an order in Finolog, from the FinologProject database, with the head method
        """
        response = self.client.head(self.finolog_projects_view)
        finolog_projects__info = FinologProject.objects.values()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(finolog_projects__info))
        self.assertEqual(response.data[0], OrderedDict(list((x, y) for x, y in finolog_projects__info[0].items())))

    def test_finolog_projects_view_and_serializer_retrieve_get_with_existent_pk(self):
        """
        Checks the operation of the retrieve function of the view and the serializer, which display data about
        projects agreed as an order in Finolog, from the FinologProject database, with the get method and with the
        existing pk
        """
        finolog_projects_info = FinologProject.objects.first()
        response = self.client.get(self.finolog_projects_view + f'{finolog_projects_info.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], finolog_projects_info.pk)
        self.assertEqual(response.data['jira_key'], finolog_projects_info.jira_key)
        self.assertEqual(response.data['finolog_id'], finolog_projects_info.finolog_id)

    def test_finolog_projects_view_and_serializer_retrieve_get_with_nonexistent_pk(self):
        """
        Checks the operation of the retrieve function of the view and the serializer, which display data about
        projects agreed as an order in Finolog, from the FinologProject database, with the get method and with the
        existing pk
        """
        response = self.client.get(self.finolog_projects_view + '11111111/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"detail": "Not found."})

    def test_finolog_projects_view_and_serializer_retrieve_head_with_existent_pk(self):
        """
        Checks the operation of the retrieve function of the view and the serializer, which display data about
        projects agreed as an order in Finolog, from the FinologProject database, with the head method and with an
        existing pk
        """
        finolog_projects_info = FinologProject.objects.first()
        response = self.client.head(self.finolog_projects_view + f'{finolog_projects_info.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], finolog_projects_info.pk)
        self.assertEqual(response.data['jira_key'], finolog_projects_info.jira_key)
        self.assertEqual(response.data['finolog_id'], finolog_projects_info.finolog_id)

    def test_finolog_projects_view_and_serializer_retrieve_head_with_nonexistent_pk(self):
        """
        Checks the operation of the retrieve function of the view and the serializer, which display data about
        projects agreed as an order in Finolog, from the FinologProject database, with the head method and with an
        existing pk
        """
        response = self.client.head(self.finolog_projects_view + '11111111/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"detail": "Not found."})

    def test_finolog_projects_view_and_serializer_creation(self):
        """
        Checks the work of the create function of the view, which validates the data and, if successful,
        creates a new record in the FinologProjects database
        At the moment, there is one project in the FinologProject database. As a result of the test, a second
        """
        response = self.client.post(self.finolog_projects_view, self.finolog_project_data_for_creation)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, FinologProject.objects.values().last())
        response_2 = self.client.get(self.finolog_projects_view)
        self.assertEqual(len(response_2.data), len(FinologProject.objects.all()))

    def test_finolog_projects_view_and_serializer_creation_with_improper_methods(self):
        """
        Checks the work of the create function of the view, which validates the data and, if successful,
        creates a new record in the FinologProjects database, with the wrong method (get instead of post) Currently,
        there is one project in the FinologProject database. As a result of the work, the creation of the second
        should not occur - instead, an existing project should be displayed
        """
        response = self.client.get(self.finolog_projects_view, self.finolog_project_data_for_creation)
        self.assertNotEqual(response.status_code, 201)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(FinologProject.objects.all()), 1)
        self.assertNotEqual(len(response.data), 2)
        self.assertNotEqual(len(FinologProject.objects.all()), 2)
        self.assertEqual(response.data[0], response.data[::-1][0])
        self.assertEqual(dict(response.data[0])['jira_key'], 'add_test')
        self.assertEqual(dict(response.data[0])['finolog_id'], '3')
        self.assertNotEqual(dict(response.data[0])['jira_key'], 'creation_test')
        self.assertNotEqual(dict(response.data[0])['finolog_id'], '1')
