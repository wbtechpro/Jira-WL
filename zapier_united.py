# Обобщенный скрипт для Запира на разбивку транзакций в Финологе для двух случаев - когда разбиние происходит по
# периоду времени и по таскам. Сочетает в себе файлы zapier.py и zapier_split_on_issues.py.

# В случае, если разбиение осуществляется по периоду времени, то на вход подаются id сотрудника, стартовая дата и
# конечная дата, при этом поле с тасками является пустым - ''.

# В случае, если разбиение осуществляется по таскам, то на вход подаются id сотрудника и таск(-и), при этом поля со
# стартовой и конечноц датами являются пустыми - ''.

# В Запире на вход подается словарь input. Здесь такое поведение эмулируется.
# В словаре все значения - строки, поэтому, при необходимости нужно явно делать приведения типов.

input = {  # данные словаря актуальны для тестовых БД и аккаунта в Финологе
    'jira_account_id': '600ab3c3dfb0c7006940d2f1',
    'date_from': '2022-03-13T00:00',
    'date_to': '2022-03-14T00:00',
    'jira_issues': '',
    'finolog_api_token': 'ez6bwR6oH7Yw5uVi62ebb1a2914e3916796e3eaa959ebcd2wYeD5PBrq6o5Vl4c',
    'finolog_transaction_id': '48105735',
    'finolog_biz_id': '45040',
    'order_type': 'out',
    'contractor_id': '3518260',
    'report_date': '2022-03-23 00:00:00',
    'category_id': '861972',
    'salary_per_hour': '20'}

import requests

# Константы
JIRA_WORKLOGS_DOMAIN = 'jira-wl.lvh.me'

# ЕСЛИ РАЗБИВАЕМ ПО ПЕРИОДУ ВРЕМЕНИ
if input['jira_issues'] == '' and input['date_from'] != '' and input['date_to'] != '':
    JIRA_WORKLOGS_URI = 'jira-client-api/grouped-worklogs'
# ЕСЛИ РАЗБИВАЕМ ПО ТАСКАМ
elif input['date_from'] == '' and input['date_to'] == '' and input['jira_issues'] != '':
    JIRA_WORKLOGS_URI = 'jira-client-api/grouped-by-issues-worklogs/'

JIRA_WORKLOGS_URL = f'http://{JIRA_WORKLOGS_DOMAIN}/{JIRA_WORKLOGS_URI}'

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
    # ЕСЛИ РАЗБИВАЕМ ПО ПЕРИОДУ ВРЕМЕНИ
    if JIRA_WORKLOGS_URI == 'jira-client-api/grouped-worklogs':
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
                worklogs_for_split[-1]['issue__project_finolog_id'] = worklog['issue__project_finolog_id']
                worklogs_for_split[-1]['issue__agreed_order_finolog__finolog_id'] = \
                    worklog['issue__agreed_order_finolog__finolog_id']

                projects_orders_and_positions[project_and_order] = len(worklogs_for_split) - 1

                worklogs_for_split[-1]['logged_time'] += worklog['logged_time']

            else:
                position = projects_orders_and_positions[project_and_order]
                worklogs_for_split[position]['logged_time'] += worklog['logged_time']

    # ЕСЛИ РАЗБИВАЕМ ПО ТАСКАМ
    elif JIRA_WORKLOGS_URI == 'jira-client-api/grouped-by-issues-worklogs/':
        # ниже список со словарями, куда будут отнесены ворклоги, сгруппированные по таскам и по заказам в Финологе,
        # либо по отсутствию заказа
        worklogs_for_split = []
        # ниже словарь соответствия заказов в Финологе и позиций словаря с ворклогами по ним в worklogs_for_split
        orders_and_positions = {}

        for worklog in wl_json['grouped_on_issues_worklogs']:
            if worklog['issue__agreed_order_finolog__finolog_id'] not in orders_and_positions.keys():
                worklogs_for_split.append({})
                worklogs_for_split[-1]['logged_time'] = 0
                worklogs_for_split[-1]['issue__agreed_order_finolog__finolog_id'] = \
                    worklog['issue__agreed_order_finolog__finolog_id']

                orders_and_positions[worklog['issue__agreed_order_finolog__finolog_id']] = len(worklogs_for_split) - 1

                worklogs_for_split[-1]['logged_time'] += worklog['logged_time']

            else:
                position = orders_and_positions[worklog['issue__agreed_order_finolog__finolog_id']]
                worklogs_for_split[position]['logged_time'] += worklog['logged_time']

    for worklog in worklogs_for_split:
        split_item = {
            "value": int(int(worklog['logged_time']) / 60 / 60 * int(input['salary_per_hour'])),
            "report_date": input['report_date'],
            "category_id": int(input['category_id']),
            "contractor_id": int(input['contractor_id']),
        }

        # ЕСЛИ РАЗБИВАЕМ ПО ПЕРИОДУ ВРЕМЕНИ
        if JIRA_WORKLOGS_URI == 'jira-client-api/grouped-worklogs':
            project_id = int(worklog['issue__project_finolog_id'])
            project_name = worklog['issue__project']
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
