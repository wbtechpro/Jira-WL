import datetime

from django.conf import settings

from client.jira_client import JiraClient
from client.helpers.helpers import (
    get_unix_time_of_prev_day_start, get_unix_time_of_prev_day_finish, get_unix_time_of_prev_week_start,
    get_unix_time_of_prev_week_finish)
from client.converters.to_percents import ToPercentByProjectsConverter
from client.converters.to_formatted_worklogs import (
    ToFormattedWorklogsConverter, ToFormattedWorklogsMergedByAuthorConverter)
from client.helpers.file_writer import write_as_json_file


# ФАЙЛ СЛОМАН!
# ОСТАВЛЕН ДЛЯ ПРИМЕРА, КАК ИСПОЛЬЗОВАТЬ КОНВЕРТЕРЫ


def load_and_process_within_last_month():
    client = JiraClient(settings.USERNAME, settings.API_TOKEN)
    data = client.get_jira_data()
    percents = ToPercentByProjectsConverter(data).convert()
    write_as_json_file(percents, settings.FILENAME_PERCENTS)


def load_and_process_within_last_week():
    """
    Merge by author. See used converter
    Also, loads WL from 00:00 Mon last week to 00:00 Tue this week (week + 1 day).
    But converted then filtrates WL by 'started' which should be within week (not 1 day).
    """
    prev_week_start = get_unix_time_of_prev_week_start()
    prev_week_finish = get_unix_time_of_prev_week_finish()
    prev_week_finish_plus_one_day = prev_week_finish + 86400000
    jira_client = JiraClient(
        settings.USERNAME, settings.API_TOKEN, since_timestamp=prev_week_start,
        until_timestamp=prev_week_finish_plus_one_day)
    jira_data = jira_client.get_jira_data()

    formatted_worklogs = ToFormattedWorklogsMergedByAuthorConverter(
        jira_data, prev_week_start, prev_week_finish).convert()
    write_as_json_file(formatted_worklogs, settings.FILENAME_WEEK_WORKLOGS)


def load_and_process_within_last_day():
    prev_day_start = get_unix_time_of_prev_day_start()
    prev_day_finish = get_unix_time_of_prev_day_finish()
    jira_client = JiraClient(
        settings.USERNAME, settings.API_TOKEN, since_timestamp=prev_day_start, until_timestamp=prev_day_finish)
    jira_data = jira_client.get_jira_data()

    formatted_worklogs = ToFormattedWorklogsConverter(jira_data).convert()
    write_as_json_file(formatted_worklogs, settings.FILENAME_DAY_WORKLOGS)


def run():
    day_number = datetime.datetime.now().day
    start_of_month = True if day_number == 1 else False
    tuesday = True if datetime.datetime.now().weekday() == 1 else False

    load_and_process_within_last_day()

    # if start_of_month:
    #     load_and_process_within_last_month()
    #
    # if tuesday:
    #     load_and_process_within_last_week()
