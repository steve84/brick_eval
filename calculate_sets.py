import argparse
import time

from functools import reduce
from sqlalchemy import create_engine, func, desc, and_, distinct, not_
from sqlalchemy.orm import sessionmaker

from models import Inventory, InventoryPart, Part, PartCategory, InventorySet, InventoryMinifig, Set
from extended_models import Score, Property, InventoryPartView, InventoryMinifigPartView


def calcScore(set_num, max_amount_of_part, parts_of_set, is_minifig=False):
    min_amount_of_part = 0

    if len(parts_of_set) == 0:
        return -1

    total_parts = reduce(lambda x, y: x + y, [x.quantity for x in parts_of_set])
    total_score = 0

    print('Calculate set with %d parts' % total_parts)

    startTime = time.time()
    for part in parts_of_set:
        part_num = part.part_num
        color_id = part.color_id
        quantity = part.quantity

        total_score += (quantity / total_parts) * pow(1 - ((part.total_quantity - min_amount_of_part) / (max_amount_of_part.total_quantity - min_amount_of_part)), 100)

    totalTime = time.time() - startTime
    print('Calculated score of set in %f seconds (%f seconds per part)' % (totalTime, totalTime / total_parts))
    return total_score


def processInventory(session, inventory_id, set_num, max_amount, is_minifig=False):
    inventory_type = 's'

    if is_minifig:
        inventory_type = 'm'

    actual_score = session.query(Score).filter(and_(
        Score.inventory_number == set_num,
        Score.inventory_type == inventory_type
    )).first()

    if is_minifig:
        parts = session.query(InventoryMinifigPartView).filter(InventoryMinifigPartView.inventory_id == inventory_id).all()
    else:
        parts = session.query(InventoryPartView).filter(InventoryPartView.inventory_id == inventory_id).all()

    score = calcScore(set_num, max_amount, parts, is_minifig)
    print('Set %s has a score of: %f' % (set_num, score))
    #import pdb;pdb.set_trace()
    if actual_score is None:
        # insert
        session.add(Score(
            inventory_id = inventory_id,
            inventory_number = set_num,
            inventory_type = inventory_type,
            needs_recalc = False,
            score = score
        ))
    elif actual_score.needs_recalc:
        # update
        actual_score.needs_recalc = False
        actual_score.score = score
    else:
        # nothing to do
        print('error')




parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--years', dest='years', type=str,
                   help='comma separated years of publication of the sets')
parser.add_argument('--themes', dest='themes', type=str,
                   help='comma separated theme ids of the sets')
parser.add_argument('--max_items', dest='max_items', type=int, default=10,
                   help='max sets to process')

themes_id = None if parser.parse_args().themes is None else parser.parse_args().themes.split(',')
years = None if parser.parse_args().years is None else parser.parse_args().years.split(',')
max_inventories = parser.parse_args().max_items

engine = create_engine('sqlite:///rebrickable.db')
Session = sessionmaker(bind=engine)
session = Session()

max_amount_set = session.query(InventoryPartView.total_quantity).order_by(desc(InventoryPartView.total_quantity)).first()
max_amount_minifig = session.query(InventoryMinifigPartView.total_quantity).order_by(desc(InventoryMinifigPartView.total_quantity)).first()

needs_recalc = session.query(Score.inventory_number).filter(Score.needs_recalc == False)
set_of_sets = session.query(InventorySet.inventory_id).distinct()

add_filters = tuple()
if years is not None:
    add_filters += (Set.year_of_publication.in_([y for y in map(lambda x: int(x), years)]),)
if themes_id is not None:
    add_filters += (Set.theme_id.in_([t for t in map(lambda x: int(x), themes_id)]),)

sets_to_check = session.query(Set.set_num).filter(*add_filters).distinct()

sets_to_calc = session.query(Inventory.id, Inventory.set_num).filter(and_(
    Inventory.set_num.notin_(needs_recalc),
    Inventory.set_num.in_(sets_to_check),
    not_(Inventory.set_num.like('fig-%')),
    Inventory.id.notin_(set_of_sets)
)).distinct()


i = 0
inventories = sets_to_calc.all()
for inventory_set in inventories:
    if i < max_inventories:
        processInventory(
            session, inventory_set.id, inventory_set.set_num,
            max_amount_set
        )
        
        fig_nums = session.query(InventoryMinifig.fig_num).filter(
            InventoryMinifig.inventory_id == inventory_set.id
        ).distinct()

        fig_inventories = session.query(Inventory.id, Inventory.set_num).filter(
            Inventory.set_num.in_(fig_nums)
        ).all()

        for inventory_minifig in fig_inventories:
            processInventory(
                session, inventory_minifig.id,
                inventory_minifig.set_num, max_amount_minifig,
                True
        )

    session.commit()
    i += 1