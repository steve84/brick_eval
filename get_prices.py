import argparse
import json
import requests
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Set

parser = argparse.ArgumentParser(description='Get prices and eol state of sets.')
parser.add_argument('--years', dest='years', type=str,
                   help='comma separated years of publication of the sets')
parser.add_argument('--themes', dest='themes', type=str,
                   help='comma separated theme ids of the sets')
parser.add_argument('--eol', dest='eol', type=str,
                    default='-1', help='comma separated eol states')
parser.add_argument('--max_items', dest='max_items', type=int, default=10,
                   help='max sets to process')

themes_id = None if parser.parse_args().themes is None else parser.parse_args().themes.split(',')
years = None if parser.parse_args().years is None else parser.parse_args().years.split(',')
eol = None if parser.parse_args().eol is None else parser.parse_args().eol.split(',')
max_items = parser.parse_args().max_items

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

add_filters = tuple()
add_filters += (Set.retail_price == None,)
if years is not None:
    add_filters += (Set.year_of_publication.in_([y for y in map(lambda x: int(x), years)]),)
if themes_id is not None:
    add_filters += (Set.theme_id.in_([t for t in map(lambda x: int(x), themes_id)]),)
if eol is not None:
    add_filters += (Set.eol.in_([e for e in map(lambda x: str(x), eol)]),)

sets = session.query(Set).filter(*add_filters).all()

i = 0
for setrow in sets:
    if i < max_items:
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
                if str(setrow.eol) not in ['2', '3']:
                    setrow.eol = '1'
        else:
            print('Setnr not found: %s' % setrow.set_num)
            setrow.eol = '0'
        i += 1


session.commit()

