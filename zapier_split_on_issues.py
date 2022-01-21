# Скрипт для Запира на разбивку транзакций в Финологе по таскам, а не по периоду времени.
# В Запире на вход подается словарь input. Здесь такое поведение эмулируется.
# В словаре все значения - строки, поэтому при необходимости нужно явно делать приведения типов

# На вход получаем айди человека, айди транзакции в Финологе, перечень тасков из Жиры через запятую

input = {  # данные словаря актуальны для тестовых БД и аккаунта в Финологе
    'jira_account_id': '60ef306b2f97d50069fb69c5',
    'jira_issues': 'LCLR-67',
    'finolog_api_token': 'T1U8BsbhvQ7KZKuv65e8413eef430e0f372f28e6bfb9190f1rmdqUcMVv2tQxxO',
    'finolog_transaction_id': '46231995',
    'finolog_biz_id': '43976',
    'order_type': 'out',
    'contractor_id': '3407655',
    'report_date': '2022-01-20 00:00:00',
    'category_id': '4',
    'salary_per_hour': '300'}

import requests

# Константы
JIRA_WORKLOGS_DOMAIN = 'jira-wl.wbtech.pro'
JIRA_WORKLOGS_URI = 'jira-client-api/grouped-by-issues-worklogs/'
JIRA_WORKLOGS_URL = f'https://{JIRA_WORKLOGS_DOMAIN}/{JIRA_WORKLOGS_URI}'

FINOLOG_TRANSACTION_INFO_URL = f'https://api.finolog.ru/v1/biz/{input["finolog_biz_id"]}/transaction/{input["finolog_transaction_id"]}'
FINOLOG_SPLIT_URL = f'https://api.finolog.ru/v1/biz/{input["finolog_biz_id"]}/transaction/{input["finolog_transaction_id"]}/split'

TRANSACTION_VALUE = None
DATA_FOR_SPLIT = {'items': []}

ERROR_CODE = None
ERROR_OUTPUT = None

#####################################################
# Получаем данные о ворклогах по таскам
wl_params = {
    'account_id': input['jira_account_id'],
    'issue__key': input['jira_issues'],
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
    for worklog in wl_json['grouped_on_issues_worklogs']:
        split_item = {
            "value": int(int(worklog['logged_time']) / 60 / 60 * int(input['salary_per_hour'])),
            "report_date": input['report_date'],
            "category_id": int(input['category_id']),
            "contractor_id": int(input['contractor_id']),
        }
        order_id = worklog['issue__agreed_order_finolog__finolog_id']
        try:
            split_item['order_id'] = int(order_id)
        except ValueError:
            pass

        DATA_FOR_SPLIT['items'].append(split_item)

# Добавляем неразбитую часть, если нужна
if not ERROR_CODE:
    split_sum = sum([i['value'] for i in DATA_FOR_SPLIT['items']])
    if split_sum <= TRANSACTION_VALUE:
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
