from .test_models_setup import FinologModelsTestsSetUp
from client.models.finolog import *


class FinologOrderModelTest(FinologModelsTestsSetUp):

    def test_string_finolog_id_jira_key_representation(self):
        """
        Проверяет работу метода __str__, который должен отражать соответствие между таском в Jira и заказом в
        Финологе (если таск является заказом сам по себе)
        """
        model_data = FinologOrder.objects.all().first()
        self.assertEqual(model_data.__str__(), 'Заказ в финологе RAND000 -- 0')

    def test_save_from_jira_finolog_tuples_method(self):
        """
        Проверяет роботу метода класса save_from_jira_finolog_tuplesб который сохраняет данные о названии таска Jira
        и id заказа из Финолога в модель FinologOrder и обновляет данные в модели IssuesInfo
        """
        tuples_data = FinologOrder.save_from_jira_finolog_tuples(self.jira_finolog_tuples)
        last_model_instance = FinologOrder.objects.all().last()
        self.assertEqual(last_model_instance.jira_key, 'RAND001')
        self.assertEqual(last_model_instance.finolog_id, '1')
        self.assertEqual(IssuesInfo.objects.all().first().agreed_order_finolog, last_model_instance)


class FinologProjectModelTest(FinologModelsTestsSetUp):

    def test_string_finolog_id_jira_key_representation(self):
        """
        Проверяет работу метода __str__, который должен отражать соответствие между проектом в Jira и заказом в Финологе
        """
        model_data = FinologProject.objects.all().first()
        self.assertEqual(model_data.__str__(), 'Проект в финологе RAND -- 222')
