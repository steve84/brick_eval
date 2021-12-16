from sqlalchemy import (
    Column,
    Integer,
    Text
)

from db import db


class ElementPriceModel(db.Model):
    __tablename__ = 'element_prices'
    __table_args__ = (
        db.Index('element_price_index', 'id',
                 'provider_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    element_id = Column(
        Integer,
        db.ForeignKey('part_color_frequency_element_rel.id'),
        nullable=False
    )
    provider_id = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)


class PartColorFrequencyElementRelation(db.Model):
    __tablename__ = 'part_color_frequency_element_rel'
    __table_args__ = (
        db.Index('pcf_element_index', 'id',
                 'part_color_frequency_id', unique=True),
    )

    id = db.Column(db.Integer, primary_key=True)
    element_id = Column(Text, nullable=False, unique=True)
    part_color_frequency_id = db.Column(db.Integer,
                                        db.ForeignKey('part_color_frequencies.id'),
                                        nullable=False)

    part_color_frequency = db.relationship('PartColorFrequencyModel',
                                           backref=db.backref('elements'))
    element_prices = db.relationship('ElementPriceModel')