import json
import requests

from requests.auth import HTTPBasicAuth

from client.helpers.helpers import get_unix_time_of_prev_month_start, get_unix_time_of_prev_month_finish
from client.helpers.list_splitter import split_list
from client.models import WorklogWithInfo, IssuesInfo


class JiraClient:

    """
    Client flowchart:
    1. get_updated_worklogs - return only ID's of recently updated worklogs.
    2. get_worklogs_info - return worklogs with full info about.
    3. get_issues_info - return issues with full info about.
        The slowest method. Makes one request for each issue's ID.
        For request uses unique issue's ID which extract from worklog info.
    4. get_woklogs_with_issues - dict with issues and worklogs
    """

    JIRA_SERVER_URL = 'https://wbtech.atlassian.net'
    JIRA_API_V3_URI = '/rest/api/3'

    def __init__(
            self, username: str = None, api_token: str = None, since_timestamp: int = None,
            jira_server_url: str = None, jira_api_uri: str = None):
        self._jira_server_url = jira_server_url or self.JIRA_SERVER_URL
        self._jira_api_uri = jira_api_uri or self.JIRA_API_V3_URI
        self.base_url = "{}{}".format(self._jira_server_url, self._jira_api_uri)
        self.auth = HTTPBasicAuth(username, api_token)
        self.since_timestamp = since_timestamp or get_unix_time_of_prev_month_start()

    def get_updated_worklogs(self) -> [int]:
        """
        Returns list of worklogs id that was updated during eager period.
        List is needed for downloading info for each worklod next to Jira client methods flowchart.
        """
        print('Starting getting worklogs ids...')

        url = self.base_url + '/worklog/updated'
        params = {'since': self.since_timestamp}
        headers = {"Accept": "application/json"}
        updated_worklog_ids = list()
        response_json = requests.get(url, params=params, headers=headers, auth=self.auth).json()
        updated_worklog_ids.extend(self._get_updated_worklogs_ids(response_json))
        while not response_json['lastPage']:
            response_json = requests.get(
                response_json['nextPage'], params=params, headers=headers, auth=self.auth).json()
            updated_worklog_ids.extend(self._get_updated_worklogs_ids(response_json))

        print(f'Got {len(updated_worklog_ids)} updated worklogs')
        return updated_worklog_ids

    def get_worklogs_info(self, updated_worklogs):
        """ Returns extended data for each worklog id """
        print('Starting getting worklogs info...')

        url = self.base_url + '/worklog/list'
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        worklogs_with_info = list()

        worklogs_by_1000 = split_list(updated_worklogs, 1000)
        for worklogs_piece in worklogs_by_1000:
            data = json.dumps({"ids": worklogs_piece})
            response_json = requests.post(url, data=data, headers=headers, auth=self.auth).json()
            worklogs_with_info.extend(response_json)
        return worklogs_with_info

    def get_issues_info(self, worklogs_with_info):
        """ Returns info about each unique issue. Makes single request for each issue_id """
        print('Starting getting issues info...')

        unique_issue_ids = set([i['issueId'] for i in worklogs_with_info])
        url = self.base_url + '/issue/'  # issue id is expected next to last "/"
        headers = {"Accept": "application/json"}

        issues_with_names = list()
        for issue_id in unique_issue_ids:
            response_json = requests.get(url + issue_id, headers=headers, auth=self.auth).json()
            issues_with_names.append(response_json)
        return issues_with_names

    def get_jira_data(self):
        updated_worklogs = self.get_updated_worklogs()
        worklogs_info = self.get_worklogs_info(updated_worklogs)
        issues_info = self.get_issues_info(worklogs_info)

        [IssuesInfo(json_data=json_data).save() for json_data in issues_info]
        print(f'Saved {len(issues_info)} issues info in DB')

        [WorklogWithInfo(json_data=json_data).save() for json_data in worklogs_info]
        print(f'Saved {len(worklogs_info)} worklogs info in DB')

        return dict(worklogs=worklogs_info, issues=issues_info)

    def _get_updated_worklogs_ids(self, response_json):
        return [int(worklog_dict['worklogId']) for worklog_dict in response_json['values']]
