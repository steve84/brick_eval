import os
import requests

url = 'https://rebrickable.com/api/v3/lego/minifigs/'
actual_page = 1

headers = dict()
headers['Accept'] = 'application/json'
headers['Authorization'] = 'key tbd'

params = dict()
params['page_size'] = 1000

total_pages = 1
result = dict()

while actual_page <= total_pages:
    params['page'] = actual_page
    print('Load next data chunk')
    req = requests.get(url, params=params, headers=headers)
    if req.status_code == 200:
        resp = req.json()
        if 'count' in resp.keys():
            total_pages = int(resp['count'] / params['page_size']) + 1
        if 'results' in resp.keys():
            for res in resp['results']:
                if res['set_img_url'] is not None:
                    base_name = os.path.basename(res['set_img_url'])
                    base_parts = base_name.split('.')
                    if len(base_parts) == 2 and not base_parts[0].startswith('fig-'):
                        result[res['set_num']] = int(base_parts[0])
        actual_page += 1
    else:
        break
        

sql_str = ''
for key, value in result.items():
    sql_str += "UPDATE minifigs SET rebrickable_id = %d WHERE fig_num = '%s';" % (value, key)

with open('rebrickable_minifigs.sql', 'w') as txt:
    txt.write(sql_str)

