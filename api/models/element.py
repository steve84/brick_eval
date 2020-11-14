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
    )

    id = Column(Integer, primary_key=True)
    element_id = Column(Text, nullable=False, unique=True)
    part_id = Column(Integer, db.ForeignKey('parts.id'), nullable=False)
    color_id = Column(Integer, db.ForeignKey('colors.id'), nullable=False)
    total_amount = Column(Integer, nullable=False, server_default='0')

    color = db.relationship('ColorModel')
    part = db.relationship('PartModel')
