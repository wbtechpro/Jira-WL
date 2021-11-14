# Скрипт для запира на разбивку транзакций в финологе. Исходные данные он получает из текущего проекта
# В запире на вход подается словарь input. Здесь такое поведение эмулируется.
# В словаре все значения - строки, поэтому, при необходимости нужно явно делать приведения типов

# На вход получаем айди человека, айди транзакции в финологе, даты от-до
input = {
    "jira_account_id": '5c671f9dcefe97640e69ba86',
    'date_from': '2021-04-01T00:00',  # Дата начала
    'date_to': '2021-04-30T23:59',  # Дата конца

    'finolog_api_token': 'TwtkzIH15gt19MRF008d56e922fa945f33916e0f3ede7f107R1Gow6ua9MX8Mfi',

    'finolog_transaction_id': '37356872',
    'finolog_biz_id': '25467',
    # token

    'order_type': 'out',  # хардкод
    'contractor_id': '1947878',  # это на вход дается, это число
    'report_date': '2021-04-27',  # эта дата тоже на вход будет приходить
    'category_id': '4',  # // это на вход дается, это число

    'salary_per_hour': '500',
}

input = {
    'jira_account_id':	'5c7c16f4fcc669199642c0ea',
    'date_from':	'2021-04-01T00:00',
    'date_to':	'2021-04-30T23:59',
    'finolog_api_token':	'TwtkzIH15gt19MRF008d56e922fa945f33916e0f3ede7f107R1Gow6ua9MX8Mfi',
    'finolog_transaction_id':	'36677058',
    'finolog_biz_id':	'25467',
    'order_type':	'out',
    'contractor_id':	'1908022',
    'category_id':	'321283',
    'salary_per_hour':	'394',
    'report_date':	'2021-04-27 00:00:00',
}


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
    for worklog in wl_json['grouped_worklogs']:
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
