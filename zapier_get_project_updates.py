import requests
import json

PROJECTS_URL = 'http://jira-wl.lvh.me/jira-client-api/finolog-projects/'

headers = {'Content-Type': 'application/json'}

data = {'jira_key': input.get('jira_key'),
        'jira_id': input.get('jira_id')}

all_projects = requests.get(PROJECTS_URL).json()

modified_project = [project for project in all_projects if data['jira_id'] == project['jira_id']][0]
modified_project_pk = modified_project['id']
modified_project_data = {'jira_key': data['jira_key'],
                         'jira_id': data['jira_id']}

response = requests.put(PROJECTS_URL + str(modified_project_pk) + '/', headers=headers,
                        data=json.dumps(modified_project_data))

output = {'code': response.status_code}
