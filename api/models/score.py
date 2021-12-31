from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    Date,
    Float,
    Text
)

from db import db


class ScoreModel(db.Model):
    __tablename__ = 'scores'

    id = Column(Integer, primary_key=True)
    inventory_id = Column(Integer,
                          db.ForeignKey('inventories.id'),
                          nullable=False)
    score = Column(Float, nullable=False)
    calc_date = Column(Date, nullable=False)

    inventory = db.relationship('InventoryModel',
                                lazy='subquery',
                                backref=db.backref('scores',
                                                   lazy=True))

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter(cls.inventory_id == _id).first()


class VScoreModel(db.Model):
    __tablename__ = 'v_scores'

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    calc_date = Column(Date, nullable=False)
    is_set = Column(Boolean, nullable=False)
    num = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    year_of_publication = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)
    num_parts = Column(Integer, nullable=False)