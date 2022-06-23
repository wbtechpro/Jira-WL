from .test_models_setup import FinologModelsTestsSetUp
from client.models.finolog import *


class FinologOrderModelTest(FinologModelsTestsSetUp):

    def test_string_finolog_id_jira_key_representation(self):
        """
        Checks the operation of the __str__ method, which should reflect the correspondence between the task in Jira
        and the order in Finolog (if the task is an order in itself)
        """
        model_data = FinologOrder.objects.all().first()
        self.assertEqual(model_data.__str__(), 'Заказ в финологе RAND000 -- 0')

    def test_save_from_jira_finolog_tuples_method(self):
        """
        Checks the robot of the save_from_jira_finolog_tuples class method, which saves data about the Jira task name
        and order id from Finolog to the FinologOrder model and updates the data in the IssuesInfo model
        """
        tuples_data = FinologOrder.save_from_jira_finolog_tuples(self.jira_finolog_tuples)
        last_model_instance = FinologOrder.objects.all().last()
        self.assertEqual(last_model_instance.jira_key, 'RAND001')
        self.assertEqual(last_model_instance.finolog_id, '1')
        self.assertEqual(IssuesInfo.objects.all().first().agreed_order_finolog, last_model_instance)


class FinologProjectModelTest(FinologModelsTestsSetUp):

    def test_string_finolog_id_jira_key_representation(self):
        """
        Checks the operation of the __str__ method, which should reflect the correspondence between the project in
        Jira and the order in Finolog
        """
        model_data = FinologProject.objects.all().first()
        self.assertEqual(model_data.__str__(), 'Проект в финологе RAND -- 222')
