import json
import requests
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Set


engine = create_engine('sqlite:///rebrickable.db')
Session = sessionmaker(bind=engine)
session = Session()

headers = {
    'x-locale': 'de-CH',
    'content-type': 'application/json',
    'user-agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
}

data = json.loads('{"operationName":"SearchSuggestions","variables":{"query":"75255","visibility":{"includeRetiredProducts":true}},"query":"query SearchSuggestions($query: String\\u0021, $suggestionLimit: Int, $productLimit: Int, $visibility: ProductVisibility) { searchSuggestions(query: $query, suggestionLimit: $suggestionLimit, productLimit: $productLimit, visibility: $visibility) { __typename ... on Product { ...Header_Product_ProductSuggestion __typename } ... on SearchSuggestion { text __typename } }}fragment Header_Product_ProductSuggestion on Product { id productCode name slug primaryImage(size: THUMBNAIL) overrideUrl ... on SingleVariantProduct { variant { ...Header_Variant_ProductSuggestion __typename } __typename } ... on MultiVariantProduct { variants { ...Header_Variant_ProductSuggestion __typename } __typename } ... on ReadOnlyProduct { readOnlyVariant { attributes { pieceCount ageRange has3DModel __typename } __typename } __typename } __typename}fragment Header_Variant_ProductSuggestion on ProductVariant { id price { formattedAmount centAmount __typename } __typename}"}')

s = requests.Session()

sets = session.query(Set).filter(
  Set.eol == '-1',
  Set.year_of_publication >= 2016
).all()

max_requests = 1000
i = 0
for setrow in sets:
  if i < max_requests:
    if i > 0 and i % 50 == 0:
        session.commit()
        time.sleep(10)
    setnr = setrow.set_num.split('-')[0]
    data['variables']['query'] = setnr
    response = s.post('https://www.lego.com/api/graphql/SearchSuggestions', headers=headers, json=data)
    json_resp = response.json()
    if 'data' in json_resp.keys() and 'searchSuggestions' in json_resp['data'].keys() and json_resp['data']['searchSuggestions'] is not None and len(json_resp['data']['searchSuggestions']) == 1:
      set_data = json_resp['data']['searchSuggestions'][0]
      if 'productCode' in set_data.keys() and 'variant' in set_data.keys() and set_data['productCode'] == setnr:
        price = set_data['variant']['price']['centAmount']
        print('%s: %d' % (setrow.set_num, price))
        setrow.retail_price = int(price)
        setrow.eol = '1'
    else:
      print('Setnr not found: %s' % setrow.set_num)
      setrow.eol = '0'
    i += 1


session.commit()
