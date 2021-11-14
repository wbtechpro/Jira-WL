import requests

from client.models import FinologApiToken, IssuesInfo


def _get_api_token():
    token = FinologApiToken.objects.first()
    if token:
        return token.token
    return 'TwtkzIH15gt19MRF008d56e922fa945f33916e0f3ede7f107R1Gow6ua9MX8Mfi'  # Старый на всяк случай


def get_finolog_orger_id_from_jira_key(jira_key):
    url = f'https://api.finolog.ru/v1/biz/25467/orders/order?description={jira_key}'
    headers = {'Api-Token': _get_api_token()}
    response = requests.get(url, headers=headers)
    if not response.status_code == 200:
        return 'не удалось запросить id заказа в финологе'
    response = response.json()
    if len(response) == 0:
        return 'не удалось найти id заказа в финологе'
    return str(response[0].get('id'))


def get_finolog_ids_for_all_jira_orders():
    order_keys = [i.get('agreed_order_key') for i in IssuesInfo.objects.unique_agreed_keys()]
    jira_finolog = []
    for jira_key in order_keys:
        finolog_id = get_finolog_orger_id_from_jira_key(jira_key)
        jira_finolog.append((jira_key, finolog_id))
    return jira_finolog