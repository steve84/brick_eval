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
    inventory_id = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    calc_date = Column(Date, nullable=False)

    def __init__(self, inventory_id, score, calc_date):
        self.inventory_id = inventory_id
        self.score = score
        self.calc_date = calc_date

    def json(self):
        return {
            'set_num': self.inventory_id,
            'score': self.score,
            'calc_date': self.calc_date
        }

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter(cls.inventory_id == _id).first()
