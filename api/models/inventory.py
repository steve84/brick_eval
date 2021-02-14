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
                 'part_id', 'color_id', 'is_spare', unique=True),
        db.Index('inventory_part_index_1',
                 'inventory_id', 'part_id', 'color_id'),
        db.Index('inventory_part_index_2', 'part_id', 'color_id'),
    )

    id = Column(Integer, primary_key=True)
    inventory_id = Column(Integer, db.ForeignKey(
        'inventories.id'), nullable=False)
    part_id = Column(Integer, db.ForeignKey('parts.id'), nullable=False)
    color_id = Column(Integer, db.ForeignKey('colors.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    is_spare = Column(Boolean, nullable=False)

    color = db.relationship('ColorModel')
    part = db.relationship('PartModel')
    part_color_frequency = db.relationship('PartColorFrequencyModel',
                                           primaryjoin="and_(InventoryPartModel.color_id==PartColorFrequencyModel.color_id, InventoryPartModel.part_id==PartColorFrequencyModel.part_id)")
    elements = db.relationship('ElementModel',
                              primaryjoin="and_(InventoryPartModel.color_id==ElementModel.color_id, InventoryPartModel.part_id==ElementModel.part_id)")


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
