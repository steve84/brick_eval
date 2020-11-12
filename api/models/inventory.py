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
    __table_args__ = (
        db.Index('inventory_index', 'version', 'set_inv_id',
                 'minifig_inv_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    version = Column(Integer, nullable=False)
    set_inv_id = Column(Integer, db.ForeignKey('inventory_sets.id'))
    minifig_inv_id = Column(Integer, db.ForeignKey('inventory_minifigs.id'))


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

    minifig = db.relationship('MinifigModel')


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
    total_quantity = Column(Integer)

    color = db.relationship('ColorModel')
    part = db.relationship('PartModel')


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
