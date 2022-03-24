# Скрипт для запира на разбивку транзакций в финологе. Исходные данные он получает из текущего проекта
# В запире на вход подается словарь input. Здесь такое поведение эмулируется.
# В словаре все значения - строки, поэтому, при необходимости нужно явно делать приведения типов

# На вход получаем айди человека, айди транзакции в финологе, даты от-до

input = {  # данные словаря актуальны для тестовых БД и аккаунта в Финологе
    'jira_account_id': '600ab3c3dfb0c7006940d2f1',
    'date_from': '2022-03-13T00:00',
    'date_to': '2022-03-14T00:00',
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
JIRA_WORKLOGS_DOMAIN = 'jira-wl.wbtech.pro'
JIRA_WORKLOGS_URI = 'jira-client-api/grouped-worklogs'
JIRA_WORKLOGS_URL = f'https://{JIRA_WORKLOGS_DOMAIN}/{JIRA_WORKLOGS_URI}'

FINOLOG_TRANSACTION_INFO_URL = f'https://api.finolog.ru/v1/biz/{input["finolog_biz_id"]}/transaction/{input["finolog_transaction_id"]}'
FINOLOG_SPLIT_URL = f'https://api.finolog.ru/v1/biz/{input["finolog_biz_id"]}/transaction/{input["finolog_transaction_id"]}/split'

TRANSACTION_VALUE = None
DATA_FOR_SPLIT = {'items': []}

ERROR_CODE = None
ERROR_OUTPUT = None

#####################################################
# Получаем данные о ворклогах
wl_params = {
    'account_id': input['jira_account_id'],
    'started_start_date': input['date_from'],
    'started_finish_date': input['date_to'],
}
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
    worklogs_without_finolog_orders = []  # список со словарями, куда будут отнесены все таски без заказа в Финологе
    worklogs_for_split = []  # список со словарями, куда будут отнесены все таски с заказом в Финологе

    # Проверка на то, подпадают ли таски, относящиеся к проекту, под заказы Финолога. Учтен случай, когда в рамках
    # одного проекта будут как таски с заказом Финолога, так и без.
    # Такие группы тасков будут отображаться отдельно друг от друга в разных строках разбиения
    for worklog in wl_json['grouped_worklogs']:
        if worklog['issue__agreed_order_finolog__finolog_id'] == 'не удалось найти id заказа в финологе':
            if not any(w['issue__project'] == worklog['issue__project'] for w in worklogs_without_finolog_orders):
                worklogs_without_finolog_orders.append({})
                worklogs_without_finolog_orders[-1]['issue__project'] = worklog['issue__project']
                worklogs_without_finolog_orders[-1]['logged_time'] = 0
                worklogs_without_finolog_orders[-1]['issue__agreed_order_finolog__finolog_id'] = 'не удалось найти id ' \
                                                                                                 'заказа в финологе '

                worklogs_without_finolog_orders[-1]['issue__agreed_order_finolog__jira_key'] = ''
                worklogs_without_finolog_orders[-1]['issue__project_finolog_id'] = worklog['issue__project_finolog_id']
            worklogs_without_finolog_orders[-1]['logged_time'] += worklog['logged_time']
        else:
            worklogs_for_split.append(worklog)

    worklogs_for_split += worklogs_without_finolog_orders  # объединяем два списка с тасками в один

    for worklog in worklogs_for_split:
        split_item = {
            "value": int(int(worklog['logged_time']) / 60 / 60 * int(input['salary_per_hour'])),
            "report_date": input['report_date'],
            "category_id": int(input['category_id']),
            "contractor_id": int(input['contractor_id']),
        }
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
