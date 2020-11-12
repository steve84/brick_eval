from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    Text
)

from db import db


class ColorModel(db.Model):
    __tablename__ = 'colors'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    rgb = Column(Text, nullable=False)
    is_trans = Column(Boolean, nullable=False)

    def __init__(self, name, rgb, is_trans):
        self.name = name
        self.rgb = rgb
        self.is_trans = is_trans

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'rgb': self.rgb,
            'is_trans': self.is_trans
        }

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter(cls.id == id).first()
