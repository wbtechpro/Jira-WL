from collections import defaultdict

from client.helpers.helpers import jira_string_time_to_unix_timestamp

# НЕ ИСПОЛЬЗУЕТСЯ - АРТЕФАКТ, ОСТАВЛЕН ДЛЯ ПРИМЕРА

class ToFormattedWorklogsConverter:

    def __init__(self, jira_data):
        self.raw_worklogs = jira_data['worklogs']
        self.raw_issues = jira_data['issues']
        self.worklogs = list()
        self.issues = list()

    def convert(self):
        self.create_cooked_worklogs()
        self.create_cooked_issues()
        self.update_worklogs_by_issues()
        return self.worklogs

    def create_cooked_worklogs(self):
        for raw_worklog in self.raw_worklogs:
            worklog = dict()
            worklog['worklog_id'] = raw_worklog['id']
            worklog['time_spent_seconds'] = raw_worklog['timeSpentSeconds']
            worklog['issue_id'] = raw_worklog['issueId']
            worklog['author'] = raw_worklog['author']['accountId']
            worklog['date'] = raw_worklog['created']
            worklog['started'] = raw_worklog['started']
            self.worklogs.append(worklog)

    def create_cooked_issues(self):
        for raw_issue in self.raw_issues:
            issue = dict()
            issue['issue_id'] = raw_issue['id']
            issue['issue_key'] = raw_issue['key']
            issue['project'] = raw_issue['key'].split('-')[0]
            issue['summary'] = raw_issue['fields']['summary']
            self.issues.append(issue)

    def update_worklogs_by_issues(self):
        """ Update dict with worklogs by info of issue from dict with issues """
        for worklog in self.worklogs:
            issue = filter(lambda issue: issue['issue_id'] == worklog['issue_id'], self.issues).__next__()
            worklog['issue_key'] = issue['issue_key']
            worklog['project'] = issue['project']
            worklog['issue_summary'] = issue['summary']
            worklog.pop('issue_id')


class ToFormattedWorklogsMergedByAuthorConverter(ToFormattedWorklogsConverter):

    def __init__(self, jira_data, started_unix_time, finished_unix_time):
        super().__init__(jira_data)
        self.started_unix_time = started_unix_time
        self.finished_unix_time = finished_unix_time

    def convert(self):
        self.worklogs = super().convert()
        self.filter_worklogs_by_started()
        self.merge_worklogs_by_author()
        return self.worklogs

    def filter_worklogs_by_started(self):
        self.worklogs = filter(
            lambda wl:
            self.started_unix_time < jira_string_time_to_unix_timestamp(wl['started']) < self.finished_unix_time,
            self.worklogs
        )

    def merge_worklogs_by_author(self):
        time_list_by_author = defaultdict(list)
        for i in self.worklogs:
            time_list_by_author[i['author']].append(i['time_spent_seconds'])
        for i in time_list_by_author:
            time_list_by_author[i] = sum(time_list_by_author[i])
        self.worklogs = time_list_by_author
