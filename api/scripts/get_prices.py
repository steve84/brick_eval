import argparse
import json
import requests
import sys
import time

from datetime import datetime, timedelta
from sqlalchemy import func


sys.path.insert(0, '../')
from db import db  # nopep8
from app import app  # nopep8

from models.set import SetModel, SetPriceModel  # nopep8

parser = argparse.ArgumentParser(
    description='Get prices and eol state of sets.'
)
parser.add_argument('--years', dest='years', type=str,
                    help='comma separated years of publication of the sets')
parser.add_argument('--themes', dest='themes', type=str,
                    help='comma separated theme ids of the sets')
parser.add_argument('--eol', dest='eol', type=str,
                    default='-1', help='comma separated eol states')
parser.add_argument('--max_days_since', dest='max_days_since', type=int,
                    default='180', help='max days since last price/eol state update')
parser.add_argument('--max_items', dest='max_items', type=int, default=10,
                    help='max sets to process')

themes_id = None if parser.parse_args(
).themes is None else parser.parse_args().themes.split(',')
years = None if parser.parse_args(
).years is None else parser.parse_args().years.split(',')
eol = None if parser.parse_args(
).eol is None else parser.parse_args().eol.split(',')
max_items = parser.parse_args().max_items
max_days_since = parser.parse_args().max_days_since

headers = {
    'x-locale': 'de-CH',
    'content-type': 'application/json',
    'origin': 'https://www.lego.com',
    'user-agent': ('Mozilla/5.0 (Windows NT 6.3; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/81.0.4044.122 Safari/537.36')
}

data = json.loads(
    ('{"operationName":"SearchSuggestions",'
     '"variables":{"query":"75255",'
     '"visibility":{"includeRetiredProducts":true}},'
     '"query":"query SearchSuggestions($query: String\\u0021, '
     '$suggestionLimit: Int, $productLimit: Int, '
     '$visibility: ProductVisibility) { searchSuggestions(query: $query, '
     'suggestionLimit: $suggestionLimit, productLimit: $productLimit, '
     'visibility: $visibility) { __typename ... on Product '
     '{ ...Header_Product_ProductSuggestion __typename } ... '
     'on SearchSuggestion { text __typename } }}fragment '
     'Header_Product_ProductSuggestion on Product { id productCode name '
     'slug primaryImage(size: THUMBNAIL) overrideUrl ... on '
     'SingleVariantProduct { variant { ...Header_Variant_ProductSuggestion '
     '__typename } __typename } ... on MultiVariantProduct { variants { '
     '...Header_Variant_ProductSuggestion __typename } __typename } ... '
     'on ReadOnlyProduct { readOnlyVariant { attributes { pieceCount '
     'ageRange has3DModel __typename } __typename } __typename } __typename}'
     'fragment Header_Variant_ProductSuggestion on ProductVariant { id price '
     '{ formattedAmount centAmount __typename } __typename}"}')
)


def isSetInResponse(json_resp, setnr):
    return ('data' in json_resp.keys() and
            'searchSuggestions' in json_resp['data'].keys() and
            json_resp['data']['searchSuggestions'] is not None and
            len(json_resp['data']['searchSuggestions']) > 0 and
            setnr in [t['productCode'] for t in json_resp['data']['searchSuggestions'] if 'productCode' in t.keys()])


def getPrice(data):
    if 'variants' in data.keys() and len(data['variants']) > 0:
        return data['variants'][0]['price']['centAmount']
    else:
        return data['variant']['price']['centAmount']


s = requests.Session()

with app.app_context():

    price_query = db.session.query(SetPriceModel.set_id, SetPriceModel.check_date, func.rank().over(partition_by=SetPriceModel.set_id, order_by=SetPriceModel.check_date.desc()).label('rnk')).subquery()

    add_filters = tuple()
    if years is not None:
        add_filters += (SetModel.year_of_publication.in_(
            [y for y in map(lambda x: int(x), years)]),)
    if themes_id is not None:
        add_filters += (SetModel.theme_id.in_(
            [t for t in map(lambda x: int(x), themes_id)]),)
    if eol is not None:
        add_filters += (SetModel.eol.in_([e for e in map(lambda x: str(x), eol)]),)
    else:
        add_filters += (SetModel.eol != 0,)


    existing_prices = list()
    if max_days_since is not None:
        price_query = db.session.query(price_query).filter(price_query.c.rnk == 1 and SetPriceModel.check_date > (datetime.now().date() - timedelta(days=max_days_since)))
        existing_prices = [x for x in map(lambda x: x.set_id, price_query.all())]


    sets = db.session.query(SetModel).filter(*add_filters).filter(SetModel.id.notin_(existing_prices)).limit(max_items).all()

    i = 0
    for setrow in sets:
        if i < max_items:
            if i > 0 and i % 50 == 0:
                db.session.commit()
                time.sleep(10)
            setnr = setrow.set_num.split('-')[0]
            data['variables']['query'] = setnr
            response = s.post(
                'https://www.lego.com/api/graphql/SearchSuggestions',
                headers=headers,
                json=data
            )
            json_resp = response.json()
            if isSetInResponse(json_resp, setnr):
                for set_data in json_resp['data']['searchSuggestions']:
                    if (('variant' in set_data.keys() or
                            'variants' in set_data.keys()) and
                            set_data['productCode'] == setnr):
                        price = getPrice(set_data)
                        print('%s: %d' % (setrow.set_num, price))
                        db.session.add(SetPriceModel(
                            set_id=setrow.id,
                            retail_price=price,
                            check_date=datetime.now().date()
                        ))
                        setrow.retail_price = int(price)
                        if str(setrow.eol) not in ['2', '3']:
                            setrow.eol = '1'

                        break
            else:
                print('Setnr not found: %s' % setrow.set_num)
                setrow.eol = '0'
            i += 1

    db.session.commit()
    db.session.close()
