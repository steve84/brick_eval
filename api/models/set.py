from sqlalchemy import (
    Column,
    Integer,
    Text,
    String
)

from db import db
from models.theme import ThemeModel


class SetModel(db.Model):
    __tablename__ = 'sets'

    id = Column(Integer, primary_key=True)
    set_num = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    year_of_publication = Column(Integer, nullable=False)
    theme_id = Column(Integer, db.ForeignKey('themes.id'), nullable=False)
    num_parts = Column(Integer, nullable=False)
    eol = Column(String(1), nullable=False, server_default='-1')
    retail_price = Column(Integer)

    theme = db.relationship('ThemeModel')

    @classmethod
    def find_by_set_num(cls, set_num):
        return cls.query.filter(cls.set_num == set_num).first()

    @classmethod
    def find_all_by_eol(cls, eol):
        return cls.query.filter(cls.eol == eol).all()
