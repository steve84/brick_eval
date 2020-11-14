import argparse
import sys
import time

from functools import reduce
from sqlalchemy import create_engine, func, desc, and_, distinct, not_
from sqlalchemy.orm import sessionmaker


sys.path.insert(0, '../')
from db import db
from app import app

from models.inventory import InventoryModel, InventoryPartModel
from models.part import PartColorFrequencyModel
from models.score import ScoreModel
from models.set import SetModel


def calcScore(session, max_amount_of_part, parts_of_set, is_minifig=False):

    if len(parts_of_set) == 0:
        return -1

    total_parts = reduce(lambda x, y: x + y, [x.quantity for x in parts_of_set])
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

        total_score += (quantity / total_parts) * pow(1 - ((part_freq.total_amount - quantity) / max_amount_of_part.total_amount), 100)

    totalTime = time.time() - startTime
    print('Calculated score of set in %f seconds (%f seconds per part)' % (totalTime, totalTime / total_parts))
    return total_score


def processInventory(session, inventory_id, max_amount, is_minifig=False):
    actual_score = session.query(ScoreModel).filter(ScoreModel.inventory_id == inventory_id).first()

    if not actual_score:
        parts = session.query(InventoryPartModel).filter(InventoryPartModel.inventory_id == inventory_id).all()

        score = calcScore(session, max_amount, parts, is_minifig)
        print('Set %d has a score of: %f' % (inventory_id, score))
        if actual_score is None:
            # insert
            session.add(ScoreModel(
                inventory_id = inventory_id,
                score = score,
                calc_date = func.current_date()
            ))
        elif actual_score.needs_recalc:
            # update
            actual_score.score = score,
            version = 1,
            actual_score.calc_date = func.current_date()
    else:
        # nothing to do
        print('Set %d already calculated' % set_id)



db.init_app(app)
with app.app_context():

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--years', dest='years', type=str,
                    help='comma separated years of publication of the sets')
    parser.add_argument('--themes', dest='themes', type=str,
                    help='comma separated theme ids of the sets')
    parser.add_argument('--max_items', dest='max_items', type=int, default=10,
                    help='max sets to process')
    parser.add_argument('--eol', dest='eol', type=str,
                    help='comma separated eol states')

    themes_id = None if parser.parse_args().themes is None else parser.parse_args().themes.split(',')
    years = None if parser.parse_args().years is None else parser.parse_args().years.split(',')
    eol = None if parser.parse_args().eol is None else parser.parse_args().eol.split(',')
    max_inventories = parser.parse_args().max_items

    max_amount = db.session.query(PartColorFrequencyModel.total_amount).order_by(desc(PartColorFrequencyModel.total_amount)).first()

    add_filters = tuple()
    if years is not None:
        add_filters += (SetModel.year_of_publication.in_([y for y in map(lambda x: int(x), years)]),)
    if themes_id is not None:
        add_filters += (SetModel.theme_id.in_([t for t in map(lambda x: int(x), themes_id)]),)
    if eol is not None:
        add_filters += (SetModel.eol.in_([e for e in map(lambda x: str(x), eol)]),)

    sets_to_check = db.session.query(SetModel.set_num).filter(*add_filters).distinct()
    sets_with_score = db.session.query(ScoreModel.inventory_id).distinct()

    sets_to_calc = db.session.query(InventoryModel.id).filter(and_(
        InventoryModel.is_latest == True,
        InventoryModel.set_id,
        InventoryModel.id.notin_(sets_with_score)
    )).all()


    i = 0
    for inventory_set in sets_to_calc:
        if i < max_inventories:
            processInventory(
                db.session, inventory_set.id, max_amount
            )
            
            # fig_nums = session.query(InventoryMinifig.fig_num).filter(
            #     InventoryMinifig.inventory_id == inventory_set.id
            # ).distinct()

            # fig_inventories = session.query(Inventory.id, Inventory.set_num).filter(
            #     Inventory.set_num.in_(fig_nums)
            # ).all()

            # for inventory_minifig in fig_inventories:
            #     processInventory(
            #         session, inventory_minifig.id,
            #         inventory_minifig.set_num, max_amount,
            #         True
            # )

        db.session.commit()
        i += 1
