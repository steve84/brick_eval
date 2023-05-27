import os
import requests

base_url = 'https://rebrickable.com/api/v3/lego/%s'

entities = ['minifigs', 'sets']
db_fields = {'minifigs': 'fig_num', 'sets': 'set_num'}

headers = dict()
headers['Accept'] = 'application/json'
headers['Authorization'] = 'key tbd'

params = dict()
params['page_size'] = 1000

result = dict()

sql_str = ''

for entity in entities:
    total_pages = 1
    actual_page = 1
    if entity not in result.keys():
        result[entity] = dict()
    while actual_page <= total_pages:
        params['page'] = actual_page
        print('Load next data %s chunk' % entity)
        req = requests.get(base_url % entity, params=params, headers=headers)
        if req.status_code == 200:
            resp = req.json()
            if 'count' in resp.keys():
                total_pages = int(resp['count'] / params['page_size']) + 1
            if 'results' in resp.keys():
                for res in resp['results']:
                    if res['set_img_url'] is not None:
                        base_name = os.path.basename(res['set_img_url'])
                        base_parts = base_name.split('.')
                        if len(base_parts) == 2:
                            try:
                                result[entity][res['set_num']] = int(base_parts[0])
                            except ValueError:
                                print('No id for %s' % res['set_num'])
            actual_page += 1
        else:
            break
        
    for key, value in result[entity].items():
        sql_str += "UPDATE %s SET rebrickable_id = %d WHERE %s = '%s';" % (entity, value, db_fields[entity], key)

with open('rebrickable_ids.sql', 'w') as txt:
    txt.write(sql_str)

