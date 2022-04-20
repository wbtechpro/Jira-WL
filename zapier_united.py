# Обобщенный скрипт для Запира на разбивку транзакций в Финологе для двух случаев - когда разбиние происходит по
# периоду времени и по таскам. Сочетает в себе файлы zapier.py и zapier_split_on_issues.py.

# В случае, если разбиение осуществляется по периоду времени, то на вход подаются id сотрудника, стартовая дата и
# конечная дата, при этом поле с тасками является пустым - 'null'.

# В случае, если разбиение осуществляется по таскам, то на вход подаются id сотрудника и таск(-и), при этом поля со
# стартовой и конечноц датами являются пустыми - 'null'.

# В Запире на вход подается словарь input. Здесь такое поведение эмулируется.
# В словаре все значения - строки, поэтому, при необходимости нужно явно делать приведения типов.

input = {  # данные словаря актуальны для тестовых БД и аккаунта в Финологе
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

# Константы
JIRA_WORKLOGS_DOMAIN = 'jira-wl.wbtech.pro'

# ЕСЛИ РАЗБИВАЕМ ПО ПЕРИОДУ ВРЕМЕНИ
if input['jira_issues'] == 'null' and input['date_from'] != 'null' and input['date_to'] != 'null':
    JIRA_WORKLOGS_URI = 'jira-client-api/grouped-worklogs'
# ЕСЛИ РАЗБИВАЕМ ПО ТАСКАМ
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
# Получаем данные о ворклогах
wl_params = {'account_id': input['jira_account_id']}

# ЕСЛИ РАЗБИВАЕМ ПО ПЕРИОДУ ВРЕМЕНИ
if JIRA_WORKLOGS_URI == 'jira-client-api/grouped-worklogs':
    wl_params['started_start_date'] = input['date_from']
    wl_params['started_finish_date'] = input['date_to']
# ЕСЛИ РАЗБИВАЕМ ПО ТАСКАМ
elif JIRA_WORKLOGS_URI == 'jira-client-api/grouped-by-issues-worklogs/':
    wl_params['issue__key'] = input['jira_issues']

wl_json = requests.get(JIRA_WORKLOGS_URL, params=wl_params).json()

#####################################################
# Удаляем сплит
headers = {'Api-Token': input['finolog_api_token']}
requests.delete(FINOLOG_SPLIT_URL, headers=headers).json()

#####################################################
# Делаем запрос на получение инфо о сумме транзакции, чтобы корректно разбить

headers = {'Api-Token': input['finolog_api_token']}
trans_info_json = requests.get(FINOLOG_TRANSACTION_INFO_URL, headers=headers).json()
TRANSACTION_VALUE = trans_info_json.get('value')
if TRANSACTION_VALUE:
    TRANSACTION_VALUE = abs(float(TRANSACTION_VALUE))
else:
    ERROR_CODE = 'error'
    ERROR_OUTPUT = 'Не удалось получить инфо о транзакции'

#####################################################
# Рассчитываем разбивку
if not ERROR_CODE:
    # ниже список со словарями, куда будут отнесены ворклоги, сгруппированные по проектам и заказам в Финологе,
    # либо по проектам и отсутствию заказа
    worklogs_for_split = []
    # ниже словарь соответствия заказов в проектах и позиций словаря с ворклогами по ним в worklogs_for_split
    projects_orders_and_positions = {}

    # Учтен случай, когда в рамках одного проекта будут как таски с заказами Финолога (в том числе разными), так и без.
    # Такие группы тасков будут отображаться отдельно друг от друга в разных строках разбиения
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
            # ЕСЛИ РАЗБИВАЕМ ПО ТАСКАМ
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

# Добавляем неразбитую часть, если нужна
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
# Делаем пост-запрос на разбивку
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
