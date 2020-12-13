from sqlalchemy import (
    Column,
    Integer,
    Date,
    Float
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
