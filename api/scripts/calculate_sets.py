import argparse
import pandas as pd
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
    MinifigInventoryRelation
)  # nopep8
from models.part import PartColorFrequencyModel  # nopep8
from models.score import ScoreModel  # nopep8
from models.set import SetModel  # nopep8
from models.statistic import StatisticModel  # nopep8
from models.theme import ThemeModel  # nopep8


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


def processInventory(session, inventory_id, max_amount, factor=1):
    actual_score = session.query(ScoreModel).filter(
        ScoreModel.inventory_id == inventory_id
    ).first()

    parts = session.query(
        InventoryPartModel.inventory_id,
        InventoryPartModel.part_id,
        InventoryPartModel.color_id,
        func.sum(InventoryPartModel.quantity * factor).label('quantity')
    ).group_by(
        InventoryPartModel.inventory_id,
        InventoryPartModel.part_id,
        InventoryPartModel.color_id
    ).filter(
        InventoryPartModel.inventory_id == inventory_id
    ).all()

    score = ScoreModel(inventory_id=inventory_id,
                       score=calcScore(session, max_amount, parts),
                       calc_date=func.current_date())

    print('Set %d has a score of: %f' % (inventory_id, score.score))
    # insert
    session.add(score)


def writeStatistics(session, scores, theme_id, max_days, is_minifig=False):
    key = 'score'
    due_date = date.today() - timedelta(days=max_days)

    act_score = session.query(StatisticModel).filter(and_(
        StatisticModel.is_set == (not is_minifig),
        StatisticModel.theme_id == (theme_id[0] if theme_id and not is_minifig else None),
        StatisticModel.property_name == 'score'
    )).first()

    if not act_score or act_score.calc_date < due_date:
        is_insert = not act_score
        if is_insert:
            act_score = StatisticModel()

        df = pd.DataFrame({key: map(lambda x: x.score, scores)})
        df_stats = df.describe()

        if df_stats[key]['count'] and df_stats[key]['count'] > 1:
            act_score.is_set = not is_minifig
            act_score.theme_id = theme_id[0] if theme_id and not is_minifig else None
            act_score.property_name = key
            act_score.count = df_stats[key]['count']
            act_score.mean = df_stats[key]['mean']
            act_score.std = df_stats[key]['std']
            act_score.min_value = df_stats[key]['min']
            act_score.lower_quartil = df_stats[key]['25%']
            act_score.median = df_stats[key]['50%']
            act_score.upper_quartil = df_stats[key]['75%']
            act_score.max_value = df_stats[key]['max']
            act_score.calc_date = func.current_date()
        else:
            return

        if is_insert:
            session.add(act_score)


def updateStatistics(session, max_days=30):
    themes = session.query(ThemeModel.id).filter(
        ThemeModel.parent_id == None  # nopep8
    ).all()

    max_scores = session.query(
        ScoreModel.id
    ).group_by(
        ScoreModel.id
    ).having(
        func.max(ScoreModel.calc_date)
    )

    scores_base = session.query(ScoreModel.score).join(
        InventoryModel,
        ScoreModel.inventory_id == InventoryModel.id,
        isouter=True
    ).join(
        SetModel,
        InventoryModel.set_id == SetModel.id,
        isouter=True
    )

    themes.append(None)
    for theme_id in themes:
        add_filters = tuple()
        add_filters += (ScoreModel.id.in_(max_scores),)
        add_filters += (ScoreModel.score >= 0,)
        add_filters += (InventoryModel.set_id != None,)  # nopep8

        if theme_id:
            add_filters += (SetModel.root_theme_id == theme_id[0],)

        scores = scores_base.filter(*add_filters).all()
        writeStatistics(session, scores, theme_id, max_days, False)

    add_filters = tuple()
    add_filters += (ScoreModel.id.in_(max_scores),)
    add_filters += (ScoreModel.score >= 0,)
    add_filters += (InventoryModel.set_id == None,)  # nopep8
    scores = scores_base.filter(*add_filters).all()
    writeStatistics(session, scores, None, max_days, True)


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
    parser.add_argument(
        '--max_days_stat', dest='max_days_stat', type=int, default=30,
        help='calculate score stats if entry older than <max_days_stat> days'
    )

    themes_id = None if parser.parse_args(
    ).themes is None else parser.parse_args().themes.split(',')
    years = None if parser.parse_args(
    ).years is None else parser.parse_args().years.split(',')
    eol = None if parser.parse_args(
    ).eol is None else parser.parse_args().eol.split(',')
    max_inventories = parser.parse_args().max_items
    max_days = parser.parse_args().max_days
    max_days_stat = parser.parse_args().max_days_stat

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
            MinifigInventoryRelation.inventory_id,
            MinifigInventoryRelation.quantity
        ).filter(
            MinifigInventoryRelation.inventory_minifig_id.in_(
                inventories_fig
            )
        ).all()

        id_quantity_map = {k: p for k, p in inventory_candidates}

        if len(inventory_candidates) > 0:
            # Works only with ScoreModel.id == None
            # Does not work ScoreModel.id is None
            fig_inventories = db.session.query(InventoryModel.id).join(
                ScoreModel,
                ScoreModel.inventory_id == InventoryModel.id,
                isouter=True
            ).filter(and_(
                InventoryModel.is_latest,
                InventoryModel.id.in_(id_quantity_map.keys()),
                or_(ScoreModel.id == None, ScoreModel.calc_date < due_date)
            )).all()  # nopep8

            for inventory_minifig in fig_inventories:
                processInventory(
                    db.session, inventory_minifig.id,
                    max_amount, factor=id_quantity_map[inventory_minifig.id]
                )

        db.session.commit()

    sql = """
        DROP VIEW IF EXISTS v_sets_scores;
        CREATE VIEW v_sets_scores AS
            SELECT DISTINCT s.id AS set_id, sc.id AS score_id FROM (
                SELECT * FROM scores
                GROUP BY inventory_id
                HAVING MAX(calc_date)
            ) SC
            LEFT JOIN inventories i ON sc.inventory_id = i.id
            LEFT JOIN sets s ON i.set_id = s.id
            WHERE s.id IS NOT NULL;
        UPDATE sets SET score_id = (
            SELECT score_id FROM v_sets_scores
            WHERE v_sets_scores.set_id = sets.id
        );
        DROP VIEW v_sets_scores;
        """

    sql += """
        DROP VIEW IF EXISTS v_inventory_minifigs_scores;
        CREATE VIEW v_inventory_minifigs_scores AS
            SELECT DISTINCT im.id AS minifig_id, sc.id AS score_id FROM (
                SELECT * FROM scores
                GROUP BY inventory_id
                HAVING MAX(calc_date)
            ) SC
            LEFT JOIN inventories i ON sc.inventory_id = i.id
            LEFT JOIN minifig_inventory_rel mir ON i.id = mir.inventory_id
            LEFT JOIN inventory_minifigs im ON mir.inventory_minifig_id = im.id
            WHERE im.id IS NOT NULL;
        UPDATE inventory_minifigs SET score_id = (
            SELECT score_id FROM v_inventory_minifigs_scores WHERE
            v_inventory_minifigs_scores.minifig_id = inventory_minifigs.id
        );
        DROP VIEW v_inventory_minifigs_scores;
        """

    conn = db.session.connection().connection
    cursor = conn.cursor()
    cursor.executescript(sql)

    updateStatistics(db.session, max_days_stat)

    db.session.commit()
