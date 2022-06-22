# A generalized script for Zapier transactions in Finolog for two cases - when splitting occurs according to time
# period and tasks. Combines zapier.py and zapier_split_on_issues.py files.

# If the splitting is carried out by a period of time, then the employee's id, start date and end date,
# while the field with tasks is empty - 'null'.

# If the splitting is carried out by tasks, then the employee id and task(s) are used as input, while the fields with
# start and end dates are empty - 'null'.

# In Zapier, the input is an input dictionary. This behavior is emulated here.
# In the dictionary, all values are strings, so if necessary, you need to explicitly cast types

input = {  # dictionary data is relevant for test databases and an account in Finolog
    'jira_account_id': '60068f460d83ff0076559478',
    'date_from': '2022-02-01T00:00',
    'date_to': '2022-02-28T23:59',
    'jira_issues': 'null',
    'finolog_api_token': 'ez6bwR6oH7Yw5uVi62ebb1a2914e3916796e3eaa959ebcd2wYeD5PBrq6o5Vl4c',
    'finolog_transaction_id': '48394062',
    'finolog_biz_id': '45040',
    'order_type': 'out',
    'contractor_id': '3518260',
    'report_date': '2022-04-01 00:00:00',
    'category_id': '861972',
    'salary_per_hour': '1000'
}

input = {
    'jira_account_id': '60068f460d83ff0076559478',
    'date_from': 'null',
    'date_to': 'null',
    'jira_issues': 'BLOG-229,BLOG-234,WBT-1355,WBT-1409',
    'finolog_api_token': 'ez6bwR6oH7Yw5uVi62ebb1a2914e3916796e3eaa959ebcd2wYeD5PBrq6o5Vl4c',
    'finolog_transaction_id': '48365059',
    'finolog_biz_id': '45040',
    'order_type': 'out',
    'contractor_id': '3518260',
    'report_date': '2022-03-31 00:00:00',
    'category_id': '861972',
    'salary_per_hour': '100'
}

input = {
    'jira_account_id': '5c671f9dcefe97640e69ba86',
    'date_from': '2021-11-01',
    'date_to': '2021-11-30',
    'jira_issues': 'null',
    'finolog_api_token': '4T35Va8JMnFJO35I982246284277c01e5122f22ed256b39b1p9ZCFg7eL4H9ZNK',
    'finolog_transaction_id': '44786236',
    'finolog_biz_id': '25467',
    'order_type': 'out',
    'contractor_id': '1947878',
    'report_date': '2021-11-27 00:00:00',
    'category_id': '1947878',
    'salary_per_hour': '455'
}
import requests

# Constants
JIRA_WORKLOGS_DOMAIN = 'jira-wl.wbtech.pro'

# IF DIVISION BY TIME PERIOD
if input['jira_issues'] == 'null' and input['date_from'] != 'null' and input['date_to'] != 'null':
    JIRA_WORKLOGS_URI = 'jira-client-api/grouped-worklogs'
# IF DIVISION BY TASKS
elif input['date_from'] == 'null' and input['date_to'] == 'null' and input['jira_issues'] != 'null':
    JIRA_WORKLOGS_URI = 'jira-client-api/grouped-by-issues-worklogs/'

JIRA_WORKLOGS_URL = f'https://{JIRA_WORKLOGS_DOMAIN}/{JIRA_WORKLOGS_URI}'

FINOLOG_TRANSACTION_INFO_URL = f'https://api.finolog.ru/v1/biz/{input["finolog_biz_id"]}/transaction/{input["finolog_transaction_id"]}'
FINOLOG_SPLIT_URL = f'https://api.finolog.ru/v1/biz/{input["finolog_biz_id"]}/transaction/{input["finolog_transaction_id"]}/split'

TRANSACTION_VALUE = None
DATA_FOR_SPLIT = {'items': []}

ERROR_CODE = None
ERROR_OUTPUT = None

#####################################################
# Getting data about worklogs
wl_params = {'account_id': input['jira_account_id']}

# IF DIVISION BY TIME PERIOD
if JIRA_WORKLOGS_URI == 'jira-client-api/grouped-worklogs':
    wl_params['started_start_date'] = input['date_from']
    wl_params['started_finish_date'] = input['date_to']
# IF DIVISION BY TASKS
elif JIRA_WORKLOGS_URI == 'jira-client-api/grouped-by-issues-worklogs/':
    wl_params['issue__key'] = input['jira_issues']

wl_json = requests.get(JIRA_WORKLOGS_URL, params=wl_params).json()

#####################################################
# Deleting split
headers = {'Api-Token': input['finolog_api_token']}
requests.delete(FINOLOG_SPLIT_URL, headers=headers).json()

#####################################################
# Making a request to receive information about the amount of the transaction in order to correctly split

headers = {'Api-Token': input['finolog_api_token']}
trans_info_json = requests.get(FINOLOG_TRANSACTION_INFO_URL, headers=headers).json()
TRANSACTION_VALUE = trans_info_json.get('value')
if TRANSACTION_VALUE:
    TRANSACTION_VALUE = abs(float(TRANSACTION_VALUE))
else:
    ERROR_CODE = 'error'
    ERROR_OUTPUT = 'Не удалось получить инфо о транзакции'

#####################################################
# Calculating splitting
if not ERROR_CODE:
    # below is a list with dictionaries, which will include worklogs grouped by projects and orders in Finolog,
    # or by projects and no order
    worklogs_for_split = []
    # below is a dictionary of matching orders in projects and dictionary positions with worklogs for them in
    # worklogs_for_split
    projects_orders_and_positions = {}

    # The case is taken into account when, within the framework of one project, there will be both tasks with
    # Finolog's orders (including different ones), and without them. Such groups of tasks will be displayed
    # separately from each other in different split lines
    for worklog in wl_json['grouped_worklogs']:
        project_and_order = worklog['issue__project'] + worklog['issue__agreed_order_finolog__finolog_id']
        if project_and_order not in projects_orders_and_positions.keys():
            worklogs_for_split.append({})
            worklogs_for_split[-1]['logged_time'] = 0
            worklogs_for_split[-1]['issue__project'] = worklog['issue__project']
            worklogs_for_split[-1]['issue__agreed_order_finolog__finolog_id'] = \
                worklog['issue__agreed_order_finolog__finolog_id']
            worklogs_for_split[-1]['issue__project_category_id'] = worklog['issue__project_category_id']
            worklogs_for_split[-1]['issue__project_finolog_id'] = worklog['issue__project_finolog_id']
            # IF DIVISION BY TASKS
            if JIRA_WORKLOGS_URI == 'jira-client-api/grouped-by-issues-worklogs/':
                worklogs_for_split[-1]['issue__key'] = worklog['issue__key']

            projects_orders_and_positions[project_and_order] = len(worklogs_for_split) - 1

            worklogs_for_split[-1]['logged_time'] += worklog['logged_time']

        else:
            position = projects_orders_and_positions[project_and_order]
            worklogs_for_split[position]['logged_time'] += worklog['logged_time']

    for worklog in worklogs_for_split:
        split_item = {
            "value": int(int(worklog['logged_time']) / 60 / 60 * int(input['salary_per_hour'])),
            "report_date": input['report_date'],
            "contractor_id": int(input['contractor_id']),
        }

        project_name = worklog['issue__project']
        project_id = int(worklog['issue__project_finolog_id'])
        if project_id == 0:
            ERROR_CODE = 'error'
            ERROR_OUTPUT = f'Нужно в сборщик ворклогов добавить связь jira-finolog для проекта {project_name}'
        else:
            split_item['project_id'] = project_id

        order_id = worklog['issue__agreed_order_finolog__finolog_id']
        try:
            split_item['order_id'] = int(order_id)
        except ValueError:
            pass

        category_id = worklog['issue__project_category_id']
        try:
            split_item['category_id'] = int(category_id)
        except ValueError:
            split_item['category_id'] = int(input['category_id'])

        DATA_FOR_SPLIT['items'].append(split_item)

# Adding unsplitted part if needed
if not ERROR_CODE:
    split_sum = sum([i['value'] for i in DATA_FOR_SPLIT['items']])
    if split_sum < TRANSACTION_VALUE:
        DATA_FOR_SPLIT['items'].append({
            "value": TRANSACTION_VALUE - split_sum,
            "report_date": input['report_date'],
            "category_id": int(input['category_id']),
            "contractor_id": int(input['contractor_id'])
        })
    elif split_sum == TRANSACTION_VALUE:
        pass
    else:
        ERROR_CODE = 'error'
        ERROR_OUTPUT = 'Сумма <ворклоги*ставка> больше размера транзакции.'

#####################################################
# Making a post-request for splitting
if not ERROR_CODE:
    headers = {
        'Accept': '*/*',
        'Api-Token': input['finolog_api_token'],
        'Content-Type': 'application/json',
    }

    finolog_response = requests.post(
        FINOLOG_SPLIT_URL,
        json=DATA_FOR_SPLIT,
        headers=headers
    )

    if not finolog_response.status_code == 200:
        ERROR_CODE = 'error'
        ERROR_OUTPUT = '{}. Код {}'.format(finolog_response.json(), finolog_response.status_code)


output = {}
if ERROR_CODE:
    output['response_code'] = ERROR_CODE
    output['response_json'] = ERROR_OUTPUT
else:
    output['response_code'] = finolog_response.status_code
    output['response_json'] = finolog_response.json()
