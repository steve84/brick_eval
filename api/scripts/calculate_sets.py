import argparse
import sys
import time

from datetime import date, timedelta
from functools import reduce
from sqlalchemy import create_engine, func, desc, and_, distinct, not_, or_
from sqlalchemy.orm import sessionmaker


sys.path.insert(0, '../')
from db import db  # nopep8
from app import app  # nopep8

from models.inventory import (
    InventoryModel,
    InventoryPartModel,
    InventoryMinifigModel,
    minifig_inventory_rel
)  # nopep8
from models.part import PartColorFrequencyModel  # nopep8
from models.score import ScoreModel  # nopep8
from models.set import SetModel  # nopep8


def calcScore(session, max_amount_of_part, parts_of_set):

    if len(parts_of_set) == 0:
        return -1

    total_parts = reduce(lambda x, y: x + y,
                         [x.quantity for x in parts_of_set])
    total_score = 0

    print('Calculate set with %d parts' % total_parts)

    startTime = time.time()
    for part in parts_of_set:
        part_id = part.part_id
        color_id = part.color_id
        quantity = part.quantity

        part_freq = session.query(PartColorFrequencyModel).filter(and_(
            PartColorFrequencyModel.color_id == color_id,
            PartColorFrequencyModel.part_id == part_id
        )).first()

        max_amount = max_amount_of_part.total_amount
        total_score += (quantity / total_parts) * pow(
            1 - ((part_freq.total_amount - quantity) / max_amount), 100)

    totalTime = time.time() - startTime
    print('Calculated score of set in %f seconds (%f seconds per part)' %
          (totalTime, totalTime / total_parts))
    return total_score


def processInventory(session, inventory_id, max_amount):
    actual_score = session.query(ScoreModel).filter(
        ScoreModel.inventory_id == inventory_id
    ).first()

    parts = session.query(InventoryPartModel).filter(
        InventoryPartModel.inventory_id == inventory_id
    ).all()

    score = calcScore(session, max_amount, parts)

    print('Set %d has a score of: %f' % (inventory_id, score))
    # insert
    session.add(ScoreModel(
        inventory_id=inventory_id,
        score=score,
        calc_date=func.current_date()
    ))


db.init_app(app)
with app.app_context():

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        '--years', dest='years', type=str,
        help='comma separated years of publication of the sets'
    )
    parser.add_argument(
        '--themes', dest='themes', type=str,
        help='comma separated theme ids of the sets'
    )
    parser.add_argument(
        '--max_items', dest='max_items', type=int, default=10,
        help='max sets to process'
    )
    parser.add_argument(
        '--eol', dest='eol', type=str,
        help='comma separated eol states'
    )
    parser.add_argument(
        '--max_days', dest='max_days', type=int, default=90,
        help='calculate set score if entry is older than <max_days> days'
    )

    themes_id = None if parser.parse_args(
    ).themes is None else parser.parse_args().themes.split(',')
    years = None if parser.parse_args(
    ).years is None else parser.parse_args().years.split(',')
    eol = None if parser.parse_args(
    ).eol is None else parser.parse_args().eol.split(',')
    max_inventories = parser.parse_args().max_items
    max_days = parser.parse_args().max_days

    due_date = date.today() - timedelta(days=max_days)

    max_amount = db.session.query(
        PartColorFrequencyModel.total_amount
    ).order_by(desc(PartColorFrequencyModel.total_amount)).first()

    add_filters = tuple()
    if years is not None:
        add_filters += (SetModel.year_of_publication.in_(
            [y for y in map(lambda x: int(x), years)]),)
    if themes_id is not None:
        add_filters += (SetModel.theme_id.in_(
            [t for t in map(lambda x: int(x), themes_id)]),)
    if eol is not None:
        add_filters += (SetModel.eol.in_(
            [e for e in map(lambda x: str(x), eol)]),)

    sets_to_check = db.session.query(
        SetModel.id
    ).filter(*add_filters).distinct()
    sets_with_score = db.session.query(ScoreModel.inventory_id).filter(
        ScoreModel.calc_date >= due_date
    ).distinct()

    sets_to_calc = db.session.query(InventoryModel.id).filter(and_(
        InventoryModel.is_latest,
        InventoryModel.set_id.in_(sets_to_check),
        InventoryModel.id.notin_(sets_with_score)
    )).limit(max_inventories).all()

    for inventory_set in sets_to_calc:
        processInventory(
            db.session, inventory_set.id, max_amount
        )

        inventories_fig = db.session.query(
            InventoryMinifigModel.id
        ).filter(
            InventoryMinifigModel.inventory_id == inventory_set.id
        )

        inventory_candidates = db.session.query(
            minifig_inventory_rel.c.inventory_id
        ).filter(
            minifig_inventory_rel.c.inventory_minifig_id.in_(
                inventories_fig
            )
        )

        # Works only with ScoreModel.id == None
        # Does not work ScoreModel.id is None
        fig_inventories = db.session.query(InventoryModel.id).join(
            ScoreModel,
            ScoreModel.inventory_id == InventoryModel.id,
            isouter=True
        ).filter(and_(
            InventoryModel.is_latest,
            InventoryModel.id.in_(inventory_candidates),
            or_(ScoreModel.id == None, ScoreModel.calc_date < due_date)
        )).all()  # nopep8

        for inventory_minifig in fig_inventories:
            processInventory(
                db.session, inventory_minifig.id,
                max_amount
            )

        db.session.commit()
