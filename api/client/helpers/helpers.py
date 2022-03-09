import time
from datetime import datetime, timedelta
from dateutil.tz import tzutc
from dateutil import parser


def get_time_by_project_from_worklog(worklogs):
    """ Merge worklogs to total time by project for each worklogs author"""
    authors_projects_time = dict()
    for worklog in worklogs:
        if not worklog['author'] in authors_projects_time:
            authors_projects_time[worklog['author']] = dict()
        if not worklog['project'] in authors_projects_time[worklog['author']]:
            authors_projects_time[worklog['author']][worklog['project']] = 0
        authors_projects_time[worklog['author']][worklog['project']] += worklog['time_spent_seconds'] / 60 / 60
    return authors_projects_time


def get_percent_by_project(time_by_project):
    """ Transforms time to percents """
    #  calculate total time
    for author in time_by_project.keys():
        time_summ = 0
        for project in time_by_project[author].keys():
            time_summ += time_by_project[author][project]
        time_by_project[author]['TOTAL'] = time_summ

    #  replace seconds to percent
    for author in time_by_project.keys():
        for project in time_by_project[author].keys():
            time_by_project[author][project] = round(
                time_by_project[author][project] / time_by_project[author]['TOTAL'] * 100)

    #  check if sum is 99 or 101 percent and make it 100
    for author in time_by_project.keys():
        del time_by_project[author]['TOTAL']
        min_project = min(time_by_project[author], key=lambda unit: time_by_project[author][unit])
        max_project = max(time_by_project[author], key=lambda unit: time_by_project[author][unit])
        total = 0
        for project in time_by_project[author].keys():
            total += time_by_project[author][project]
        if total > 100:
            time_by_project[author][max_project] -= 1
        elif total < 100:
            time_by_project[author][min_project] += 1
    return time_by_project


def unite_wbtech_projects(percents_by_project_by_author):
    wbtech_projects = ['DPO', 'JIRA', 'REC', 'TEST', 'WS', 'WBT', 'FIN', 'BLOG']
    for author in percents_by_project_by_author.keys():
        percents_by_project = percents_by_project_by_author[author]
        projects_to_unite = list(filter(lambda x: x in wbtech_projects, percents_by_project.keys()))
        wbtech_sum_percent = sum(map(lambda x: percents_by_project[x], projects_to_unite))
        for project in projects_to_unite:
            del percents_by_project[project]
        if wbtech_sum_percent != 0:
            percents_by_project['WBT'] = wbtech_sum_percent
    return percents_by_project_by_author


def get_unix_time_of_prev_month_start():
    tz_utc = tzutc()
    now = datetime.now()
    start_of_prev_month = now - timedelta(days=28)
    start_of_prev_month = datetime(
        year=start_of_prev_month.year, month=start_of_prev_month.month, day=1, tzinfo=tz_utc)
    start_of_prev_month = int(time.mktime(start_of_prev_month.timetuple())) * 1000
    return start_of_prev_month


def get_unix_time_of_prev_month_finish():
    tz_utc = tzutc()
    now = datetime.now()
    finish_of_prev_month = datetime(year=now.year, month=now.month, day=1, tzinfo=tz_utc)
    finish_of_prev_month = int(time.mktime(finish_of_prev_month.timetuple())) * 1000
    return finish_of_prev_month


def get_unix_time_of_prev_day_start():
    tz_utc = tzutc()
    now = datetime.now()
    start_of_prev_day = now - timedelta(days=1)
    start_of_prev_day = datetime(
        year=start_of_prev_day.year, month=start_of_prev_day.month, day=start_of_prev_day.day, tzinfo=tz_utc)
    start_of_prev_day = int(time.mktime(start_of_prev_day.timetuple())) * 1000
    return start_of_prev_day


def get_unix_time_of_prev_day_finish():
    prev_day_start = get_unix_time_of_prev_day_start()
    return prev_day_start + 86400000


def get_unix_time_of_prev_week_start():
    tz_utc = tzutc()
    now = datetime.now()
    start_of_prev_week = now - timedelta(days=(7 + now.weekday()))
    start_of_prev_week = datetime(
        year=start_of_prev_week.year, month=start_of_prev_week.month, day=start_of_prev_week.day, tzinfo=tz_utc)
    start_of_prev_week = int(time.mktime(start_of_prev_week.timetuple())) * 1000
    return start_of_prev_week


def get_unix_time_of_prev_week_finish():
    prev_week_start = get_unix_time_of_prev_week_start()
    return prev_week_start + (86400000 * 7)


def jira_string_time_to_unix_timestamp(stringtime):
    date_time = parser.parse(stringtime)
    return int(time.mktime(date_time.timetuple())) * 1000


def get_unix_time_n_days_before_date(n, start_date):
    end_date = start_date - timedelta(days=n)
    end_date_unix = int(time.mktime(end_date.timetuple())) * 1000
    start_date_unix = int(time.mktime(start_date.timetuple())) * 1000
    return end_date_unix, start_date_unix
