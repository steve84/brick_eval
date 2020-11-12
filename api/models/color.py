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

    @classmethod
    def find_by_id(cls, id: int) -> "ColorModel":
        return cls.query.filter(cls.id == id).first()
