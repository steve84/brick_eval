import json
import requests

headers = {
    'x-locale': 'de-CH',
    'content-type': 'application/json',
}

data = json.loads('{"operationName":"SearchSuggestions","variables":{"query":"75255","visibility":{"includeRetiredProducts":true}},"query":"query SearchSuggestions($query: String\\u0021, $suggestionLimit: Int, $productLimit: Int, $visibility: ProductVisibility) { searchSuggestions(query: $query, suggestionLimit: $suggestionLimit, productLimit: $productLimit, visibility: $visibility) { __typename ... on Product { ...Header_Product_ProductSuggestion __typename } ... on SearchSuggestion { text __typename } }}fragment Header_Product_ProductSuggestion on Product { id productCode name slug primaryImage(size: THUMBNAIL) overrideUrl ... on SingleVariantProduct { variant { ...Header_Variant_ProductSuggestion __typename } __typename } ... on MultiVariantProduct { variants { ...Header_Variant_ProductSuggestion __typename } __typename } ... on ReadOnlyProduct { readOnlyVariant { attributes { pieceCount ageRange has3DModel __typename } __typename } __typename } __typename}fragment Header_Variant_ProductSuggestion on ProductVariant { id price { formattedAmount centAmount __typename } __typename}"}')

s = requests.Session()

sets = ['21039','21047','75232','40354']
for set in sets:
  data['variables']['query'] = set
  response = s.post('https://www.lego.com/api/graphql/SearchSuggestions', headers=headers, json=data)
  json_resp = response.json()
  if 'data' in json_resp.keys() and 'searchSuggestions' in json_resp['data'].keys() and len(json_resp['data']['searchSuggestions']) == 1:
    print('%s: %d' % (set, json_resp['data']['searchSuggestions'][0]['variant']['price']['centAmount']))
