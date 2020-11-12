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

    sub_theme = db.relationship('ThemeModel', lazy='dynamic')

    def __init__(self, name, parent_id):
        self.name = name
        self.parent_id = parent_id

    def json(self):
        return {'name': self.name}
