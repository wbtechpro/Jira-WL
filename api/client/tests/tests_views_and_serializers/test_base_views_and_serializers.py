import dateutil.parser
from collections import OrderedDict

from .test_views_and_serializers_setup import ViewsAndSerializersTestSetUp
from client.models import IssuesInfo, WorklogWithInfo


class WorklogsBaseViewAndSerializer(ViewsAndSerializersTestSetUp):

    def test_worklogs_info_display_get(self):
        """
        Проверяет работу вью и сериализатора, которые отображают информацию о ворклогах из Jira, с методом get
        """
        response = self.client.get(self.base_worklogs_view)
        worklogs_info = WorklogWithInfo.objects.values(*self.test_data_worklog_fields)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['id'], worklogs_info[0]['id'])  # сравнение полей сделано вручную, так как
        # в ответе с сервера все даты и время отображаются в формате ISO 8601
        self.assertEqual(response.data[0]['url'], worklogs_info[0]['url'])
        self.assertEqual(response.data[0]['display_name'], worklogs_info[0]['display_name'])
        self.assertEqual(response.data[0]['account_id'], worklogs_info[0]['account_id'])
        self.assertEqual(dateutil.parser.isoparse(response.data[0]['created']), worklogs_info[0]['created'])
        self.assertEqual(dateutil.parser.isoparse(response.data[0]['updated']), worklogs_info[0]['updated'])
        self.assertEqual(dateutil.parser.isoparse(response.data[0]['started']), worklogs_info[0]['started'])
        self.assertEqual(response.data[0]['time_spent_seconds'], worklogs_info[0]['time_spent_seconds'])
        self.assertEqual(response.data[0]['time_spent'], worklogs_info[0]['time_spent'])
        self.assertEqual(response.data[0]['jira_id'], worklogs_info[0]['jira_id'])
        self.assertEqual(response.data[0]['issueId'], worklogs_info[0]['issueId'])
        self.assertEqual(response.data[0]['issue'], worklogs_info[0]['issue'])

    def test_worklogs_info_display_head(self):
        """
        Проверяет работу вью и сериализатора, которые отображают информацию о ворклогах из Jira, с методом get
        """
        response = self.client.head(self.base_worklogs_view)
        worklogs_info = WorklogWithInfo.objects.values(*self.test_data_worklog_fields)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['id'], worklogs_info[0]['id'])  # сравнение полей сделано вручную, так как
        # в ответе с сервера все даты и время отображаются в формате ISO 8601
        self.assertEqual(response.data[0]['url'], worklogs_info[0]['url'])
        self.assertEqual(response.data[0]['display_name'], worklogs_info[0]['display_name'])
        self.assertEqual(response.data[0]['account_id'], worklogs_info[0]['account_id'])
        self.assertEqual(dateutil.parser.isoparse(response.data[0]['created']), worklogs_info[0]['created'])
        self.assertEqual(dateutil.parser.isoparse(response.data[0]['updated']), worklogs_info[0]['updated'])
        self.assertEqual(dateutil.parser.isoparse(response.data[0]['started']), worklogs_info[0]['started'])
        self.assertEqual(response.data[0]['time_spent_seconds'], worklogs_info[0]['time_spent_seconds'])
        self.assertEqual(response.data[0]['time_spent'], worklogs_info[0]['time_spent'])
        self.assertEqual(response.data[0]['jira_id'], worklogs_info[0]['jira_id'])
        self.assertEqual(response.data[0]['issueId'], worklogs_info[0]['issueId'])
        self.assertEqual(response.data[0]['issue'], worklogs_info[0]['issue'])

    def test_worklogs_info_display_prohibited_methods(self):
        """
        Проверяет, что вью не работает с http-методами, помимо указанных (get, head)
        """
        response = self.client.post(self.base_worklogs_view)
        self.assertEqual(response.status_code, 405)

    def test_worklogs_data_filters_dates(self):
        """
        Проверяет работу фильтра, который отбирает значения по полям updated_start_date, updated_finish_date,
        created_start_date, created_finish_date, started_start_date, started_finish_date
        Конкретно в этом тесте проверяется фильтрация по двум параметрам: created_start_date и started_finish_date
        """
        response = self.client.get(self.base_worklogs_view + '?updated=&started=&created=&account_id=&issue__project'
                                                             '=&issue__key=&updated_start_date=&updated_finish_date'
                                                             '=&created_start_date=2022-01-01T10%3A00%3A00'
                                                             '&created_finish_date=&started_start_date'
                                                             '=&started_finish_date=2022-01-01T10%3A00%3A00')
        worklogs_info = WorklogWithInfo.objects.filter(created='2022-01-01 10:00:00') \
            .filter(started='2022-01-01 09:00:00').values()
        self.assertEqual(len(WorklogWithInfo.objects.all()), 3)
        self.assertEqual(len(worklogs_info), 2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], worklogs_info[0]['id'])
        self.assertEqual(response.data[1]['id'], worklogs_info[1]['id'])

    def test_worklogs_data_filters_account_id(self):
        """
        Проверяет работу фильтра, который отбирает значения по полю account_id
        """
        response = self.client.get(self.base_worklogs_view + '?updated=&started=&created=&account_id=1&issue__project'
                                                             '=&issue__key=&updated_start_date=&updated_finish_date'
                                                             '=&created_start_date=&created_finish_date'
                                                             '=&started_start_date=&started_finish_date=')
        worklogs_info = WorklogWithInfo.objects.filter(account_id=1).values()
        self.assertEqual(len(WorklogWithInfo.objects.all()), 3)
        self.assertEqual(len(worklogs_info), 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], worklogs_info[0]['id'])

    def test_worklogs_data_filters_issue__project(self):
        """
        Проверяет работу фильтра, который отбирает значения по полю issue__project
        """
        response = self.client.get(self.base_worklogs_view + '?updated=&started=&created=&account_id=&issue__project'
                                                             '=add_test&issue__key=&updated_start_date'
                                                             '=&updated_finish_date=&created_start_date'
                                                             '=&created_finish_date=&started_start_date'
                                                             '=&started_finish_date=')
        worklogs_info = WorklogWithInfo.objects.filter(issue__project='add_test').values()
        self.assertEqual(len(WorklogWithInfo.objects.all()), 3)
        self.assertEqual(len(worklogs_info), 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_worklogs_data_filters_single_issue__key(self):
        """
        Проверяет работу фильтра, который отбирает значения по полю issue__key
        В данном тесте проверяется случай, когда ищется один таск
        """
        response = self.client.get(self.base_worklogs_view + '?updated=&started=&created=&account_id=&issue__project'
                                                             '=&issue__key=add_test-234&updated_start_date'
                                                             '=&updated_finish_date=&created_start_date'
                                                             '=&created_finish_date=&started_start_date'
                                                             '=&started_finish_date=')
        worklogs_info = WorklogWithInfo.objects.filter(issue__key='add_test-234').values()
        self.assertEqual(len(WorklogWithInfo.objects.all()), 3)
        self.assertEqual(len(worklogs_info), 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_worklogs_data_filters_multiple_issues__keys(self):
        """
        Проверяет работу фильтра, который отбирает значения по полю issue__key
        В данном тесте проверяется случай, когда ищется несколько тасков
        """
        response = self.client.get(self.base_worklogs_view + '?updated=&started=&created=&account_id=&issue__project'
                                                             '=&issue__key=add_test-234, test-123&updated_start_date'
                                                             '=&updated_finish_date=&created_start_date'
                                                             '=&created_finish_date=&started_start_date'
                                                             '=&started_finish_date=')
        worklogs_info = WorklogWithInfo.objects.filter(issue__key__in=('add_test-234', 'test-123')).values()
        self.assertEqual(len(WorklogWithInfo.objects.all()), 3)
        self.assertEqual(len(worklogs_info), 2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)


class IssueBaseViewAndSerializer(ViewsAndSerializersTestSetUp):

    def test_issues_info_display_get(self):
        """
        Проверяет работу вью и сериализатора, которые отображают информацию о тасках из Jira, с методом get
        """
        response = self.client.get(self.base_issues_view)
        issue_info = IssuesInfo.objects.values(*self.test_data_issue_fields)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0], OrderedDict(list((x, y) for x, y in issue_info[0].items())))

    def test_issues_info_display_head(self):
        """
        Проверяет работу вью и сериализатора, которые отображают информацию о тасках из Jira, с методом head
        """
        response = self.client.head(self.base_issues_view)
        issue_info = IssuesInfo.objects.values(*self.test_data_issue_fields)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0], OrderedDict(list((x, y) for x, y in issue_info[0].items())))

    def test_issues_info_display_prohibited_methods(self):
        """
        Проверяет, что вью не работает с http-методами, помимо указанных (get, head)
        """
        response = self.client.post(self.base_issues_view)
        self.assertEqual(response.status_code, 405)

    def test_issues_data_filter_by_key(self):
        """
        Проверяет работу фильтра, который отбирает значения по полю key
        """
        response = self.client.get(self.base_issues_view + '?key=test-123')
        issue_info = IssuesInfo.objects.filter(key='test-123').values()
        self.assertEqual(len(IssuesInfo.objects.all()), 3)
        self.assertEqual(len(issue_info), 2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['key'], issue_info[0]['key'])
        self.assertEqual(response.data[1]['key'], issue_info[1]['key'])
