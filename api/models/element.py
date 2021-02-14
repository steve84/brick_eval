from sqlalchemy import (
    Column,
    Integer,
    Text
)

from db import db


class ElementModel(db.Model):
    __tablename__ = 'elements'
    __table_args__ = (
        db.Index('element_index', 'element_id',
                 'part_id', 'color_id', unique=True),
        db.ForeignKeyConstraint(
            ['part_id', 'color_id'],
            ['inventory_parts.part_id', 'inventory_parts.color_id']
        ),
    )

    id = Column(Integer, primary_key=True)
    element_id = Column(Text, nullable=False, unique=True)
    part_id = Column(Integer, db.ForeignKey('parts.id'), nullable=False)
    color_id = Column(Integer, db.ForeignKey('colors.id'), nullable=False)

    color = db.relationship('ColorModel')
    part = db.relationship('PartModel')
    prices = db.relationship('ElementPriceModel')


class ElementPriceModel(db.Model):
    __tablename__ = 'element_prices'
    __table_args__ = (
        db.Index('element_price_index', 'element_id',
                 'provider_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    element_id = Column(
        Text,
        db.ForeignKey('elements.element_id'),
        nullable=False
    )
    provider_id = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
