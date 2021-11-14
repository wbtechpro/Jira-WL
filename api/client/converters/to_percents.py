from django.conf import settings

from client.helpers.helpers import (
    get_time_by_project_from_worklog, get_percent_by_project, unite_wbtech_projects)

# НЕ ИСПОЛЬЗУЕТСЯ - АРТЕФАКТ, ОСТАВЛЕН ДЛЯ ПРИМЕРА


class ToPercentByProjectsConverter:

    def __init__(self, jira_data):
        self.raw_worklogs = jira_data['worklogs']
        self.raw_issues = jira_data['issues']
        self.worklogs = list()
        self.issues = list()

    def convert(self):
        self.create_cooked_worklogs()
        self.create_cooked_issues()
        self.update_worklogs_by_issues()
        time_by_projects = get_time_by_project_from_worklog(self.worklogs)
        percent_by_projects = get_percent_by_project(time_by_projects)
        percent_by_projects_united_by_wbtech = unite_wbtech_projects(percent_by_projects)
        return percent_by_projects_united_by_wbtech

    def create_cooked_worklogs(self):
        filtered_worklog = self._exclude_by_authors_ids()
        for raw_worklog in filtered_worklog:
            worklog = dict()
            worklog['worklog_id'] = raw_worklog['id']
            worklog['time_spent_seconds'] = raw_worklog['timeSpentSeconds']
            worklog['issue_id'] = raw_worklog['issueId']
            worklog['author'] = raw_worklog['author']['accountId']
            self.worklogs.append(worklog)

    def create_cooked_issues(self):
        for raw_issue in self.raw_issues:
            issue = dict()
            issue['issue_id'] = raw_issue['id']
            issue['issue_key'] = raw_issue['key']
            issue['project'] = raw_issue['key'].split('-')[0]
            self.issues.append(issue)

    def update_worklogs_by_issues(self):
        """ Update dict with worklogs by info of issue from dict with issues """
        for worklog in self.worklogs:
            issue = filter(lambda issue: issue['issue_id'] == worklog['issue_id'], self.issues).__next__()
            worklog['issue_key'] = issue['issue_key']
            worklog['project'] = issue['project']

    def _exclude_by_authors_ids(self):
        if settings.TO_PERCENT_ID_FOR_EXCLUDE:
            return list(filter(
                lambda raw_worklog: raw_worklog['author']['accountId'] not in settings.TO_PERCENT_ID_FOR_EXCLUDE,
                self.raw_worklogs))
        return self.raw_worklogs
