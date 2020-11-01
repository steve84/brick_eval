import json
import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Set


engine = create_engine('sqlite:///rebrickable.db')
Session = sessionmaker(bind=engine)
session = Session()

headers = {
    'x-locale': 'de-CH',
    'content-type': 'application/json',
}

data = json.loads('{"operationName":"SearchSuggestions","variables":{"query":"75255","visibility":{"includeRetiredProducts":true}},"query":"query SearchSuggestions($query: String\\u0021, $suggestionLimit: Int, $productLimit: Int, $visibility: ProductVisibility) { searchSuggestions(query: $query, suggestionLimit: $suggestionLimit, productLimit: $productLimit, visibility: $visibility) { __typename ... on Product { ...Header_Product_ProductSuggestion __typename } ... on SearchSuggestion { text __typename } }}fragment Header_Product_ProductSuggestion on Product { id productCode name slug primaryImage(size: THUMBNAIL) overrideUrl ... on SingleVariantProduct { variant { ...Header_Variant_ProductSuggestion __typename } __typename } ... on MultiVariantProduct { variants { ...Header_Variant_ProductSuggestion __typename } __typename } ... on ReadOnlyProduct { readOnlyVariant { attributes { pieceCount ageRange has3DModel __typename } __typename } __typename } __typename}fragment Header_Variant_ProductSuggestion on ProductVariant { id price { formattedAmount centAmount __typename } __typename}"}')

s = requests.Session()

sets = session.query(Set).filter(
  Set.retail == None,
  Set.year_of_publication >= 2019
).all()

max_requests = 250
i = 0
for setrow in sets:
  if i < max_requests:
    setnr = setrow.set_num.split('-')[0]
    data['variables']['query'] = setnr
    response = s.post('https://www.lego.com/api/graphql/SearchSuggestions', headers=headers, json=data)
    json_resp = response.json()
    if 'data' in json_resp.keys() and 'searchSuggestions' in json_resp['data'].keys() and json_resp['data']['searchSuggestions'] is not None and len(json_resp['data']['searchSuggestions']) == 1:
      set_data = json_resp['data']['searchSuggestions'][0]
      if 'productCode' in set_data.keys() and 'variant' in set_data.keys() and set_data['productCode'] == setnr:
        price = set_data['variant']['price']['centAmount']
        print('%s: %d' % (setrow.set_num, price))
        setrow.retail = int(price)
        setrow.eol = False
    else:
      print('Setnr not found: %s' % setrow.set_num)
      setrow.retail = -1
      setrow.eol = True
    i += 1


session.commit()
