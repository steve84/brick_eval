from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean
)

from db import db
from models.set import SetModel


class InventoryModel(db.Model):
    __tablename__ = 'inventories'

    id = Column(Integer, primary_key=True)
    set_id = Column(Integer, db.ForeignKey('sets.id'))
    version = Column(Integer, nullable=False)
    is_latest = Column(Boolean, nullable=False, server_default='1')

    set = db.relationship('SetModel',
                          lazy='subquery',
                          backref=db.backref('inventories',
                                             lazy=True))

    inventory_sets = db.relationship('InventorySetModel',
                                     lazy='subquery',
                                     backref=db.backref('inventories',
                                                        lazy=True))

    inventory_minifigs = db.relationship('InventoryMinifigModel',
                                         lazy='subquery',
                                         backref=db.backref('inventories',
                                                            lazy=True))


class InventoryMinifigModel(db.Model):
    __tablename__ = 'inventory_minifigs'
    __table_args__ = (
        db.Index('inventory_minifig_index',
                 'inventory_id', 'fig_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    inventory_id = Column(Integer, db.ForeignKey(
        'inventories.id'), nullable=False)
    fig_id = Column(Integer, db.ForeignKey('minifigs.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    score_id = Column(Integer, db.ForeignKey('scores.id'))

    minifig = db.relationship('MinifigModel')
    score = db.relationship('ScoreModel')

    inventory_minifig_rel = db.relationship('MinifigInventoryRelation')


class InventoryPartModel(db.Model):
    __tablename__ = 'inventory_parts'
    __table_args__ = (
        db.Index('inventory_part_index', 'inventory_id',
                 'part_color_frequency_id', 'is_spare', unique=True),
        db.Index('inventory_part_index_1',
                 'inventory_id', 'part_color_frequency_id'),
    )

    id = Column(Integer, primary_key=True)
    inventory_id = Column(Integer, db.ForeignKey(
        'inventories.id'), nullable=False)
    part_color_frequency_id = Column(Integer, db.ForeignKey(
        'part_color_frequencies.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    is_spare = Column(Boolean, nullable=False)

    part_color_frequency = db.relationship('PartColorFrequencyModel')


class VInventoryPartModel(db.Model):
    __tablename__ = 'v_inventory_parts'

    id = Column(Integer, primary_key=True)
    inventory_id = Column(Integer, nullable=False)
    part_num = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    part_material = Column(Text, nullable=False)
    is_spare = Column(Boolean, nullable=False)
    quantity = Column(Integer, nullable=False)
    color_name = Column(Text, nullable=False)
    rgb = Column(Text, nullable=False)
    is_trans = Column(Boolean, nullable=False)
    total_amount = Column(Integer, nullable=False)
    element_id = Column(Integer)


class InventorySetModel(db.Model):
    __tablename__ = 'inventory_sets'
    __table_args__ = (
        db.Index('inventory_set_index', 'inventory_id', 'set_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    inventory_id = Column(Integer, db.ForeignKey(
        'inventories.id'), nullable=False)
    set_id = Column(Integer, db.ForeignKey('sets.id'), nullable=False)
    quantity = Column(Integer, nullable=False)

    set = db.relationship('SetModel')


class SetInventoryRelation(db.Model):
    __tablename__ = 'set_inventory_rel'

    id = db.Column(db.Integer, primary_key=True)
    inventory_set_id = db.Column(db.Integer,
                                 db.ForeignKey('inventory_sets.id'))
    inventory_id = db.Column(db.Integer,
                             db.ForeignKey('inventories.id'))


class MinifigInventoryRelation(db.Model):
    __tablename__ = 'minifig_inventory_rel'

    id = db.Column(db.Integer, primary_key=True)
    inventory_minifig_id = db.Column(db.Integer,
                                     db.ForeignKey('inventory_minifigs.id'))
    inventory_id = db.Column(db.Integer,
                             db.ForeignKey('inventories.id'))
    quantity = Column(Integer, nullable=False)
