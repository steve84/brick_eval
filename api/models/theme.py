from sqlalchemy import (
    Column,
    Integer,
    Text,
    Numeric,
    DECIMAL
)

from db import db


class ThemeModel(db.Model):
    __tablename__ = 'themes'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    parent_id = Column(DECIMAL(4, 1), db.ForeignKey('themes.id'))

    children = db.relationship("ThemeModel",
                               backref=db.backref('parent', remote_side=[id]))
