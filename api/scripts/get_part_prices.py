import argparse
import requests
import sys
import re
import pandas as pd
import itertools

from sqlalchemy import and_

sys.path.insert(0, '../')
from db import db  # nopep8
from app import app  # nopep8

from models.element import ElementModel, ElementPriceModel  # nopep8
from models.part import PartModel  # nopep8


def toDesignId(nbr):
    if nbr.find('-1') > -1:
        return nbr
    else:
        p = re.search(r'^\d{4,5}', nbr)
        if p is not None:
            return p.group()
        else:
            return None


def insertPrice(session, id, provider_id, price):
    print(
        'Insert element %s' % id
    )
    session.add(ElementPriceModel(
        element_id=id,
        provider_id=provider_id,
        price=price
    ))


parser = argparse.ArgumentParser(
    description='Get part prices.'
)
parser.add_argument('--max_items', dest='max_items', type=int, default=10,
                    help='max sets to process')

max_items = parser.parse_args().max_items

url = 'https://bricksandpieces.services.lego.com/api/v1/bricks/%s/%s'

params = dict()
params['country'] = 'CH'
params['orderType'] = 'buy'

headers = dict()
headers['x-api-key'] = 'saVSCq0hpuxYV48mrXMGfdKnMY1oUs3s'


db.init_app(app)
with app.app_context():
    element_prices = db.session.query(ElementPriceModel.element_id)

    element_list = db.session.query(
        PartModel.part_num,
        ElementModel.element_id
    ).join(
        ElementModel,
        PartModel.id == ElementModel.part_id,
        isouter=True
    ).filter(and_(
        PartModel.part_num.notlike('0%'),
        PartModel.part_cat_id.notin_([58]),
        ElementModel.element_id != None,  # nopep8
        ElementModel.element_id.notin_(element_prices)
    )).distinct().limit(max_items).all()

    element_list = sorted(element_list, key=lambda x: x[0])
    element_dict = {
        toDesignId(k): [p1[1] for p1 in p]
        for k, p in itertools.groupby(element_list, lambda x: x[0])
    }
    i = 0
    for ele in element_dict.keys():
        if i < max_items and ele is not None:
            resp = requests.get(
                url % ('items', ele),
                headers=headers,
                params=params
            )

            if resp.status_code == 200 and 'bricks' in resp.json():
                df = pd.DataFrame(resp.json()['bricks'])
                db_element_ids = element_dict[ele]
                for index, row in df.iterrows():
                    if row['itemNumber'] in db_element_ids:
                        db_element_ids.remove(row['itemNumber'])
                    price_id = db.session.query(ElementPriceModel.id).filter(
                        ElementPriceModel.element_id == row['itemNumber']
                    ).first()

                    if price_id is None:
                        i += 1
                        insertPrice(
                            db.session,
                            row['itemNumber'],
                            1,
                            int(float(row['price']['amount']) * 100)
                        )

                for db_id in db_element_ids:
                    price_id = db.session.query(ElementPriceModel.id).filter(
                        ElementPriceModel.element_id == db_id
                    ).first()

                    if price_id is None:
                        insertPrice(
                            db.session,
                            db_id,
                            1,
                            -1
                        )

            elif resp.status_code == 204:
                print('Element %s not found' % ele)
                for ele2 in element_dict[ele]:
                    insertPrice(
                        db.session,
                        ele2,
                        1,
                        -1
                    )
            else:
                print('Another problem: %d' % resp.status_code)

    if None in element_dict.keys():
        for ele2 in element_dict[None]:
            insertPrice(
                db.session,
                ele2,
                1,
                -1
            )

    db.session.commit()
    db.session.close()
