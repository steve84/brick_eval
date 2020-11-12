from sqlalchemy import (
    Column,
    Integer,
    Text,
    String
)

from db import db


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

    def __init__(self, set_num, name, year_of_publication, theme_id,
                 num_parts, eol, retail_price):
        self.set_num = set_num
        self.name = name
        self.year_of_publication = year_of_publication
        self.theme_id = theme_id
        self.num_parts = num_parts
        self.eol = eol
        self.retail_price = retail_price

    def json(self):
        return {
            'set_num': self.set_num,
            'name': self.name,
            'year': self.year_of_publication,
            'num_parts': self.num_parts,
            'eol': self.eol,
            'price': self.retail_price / 100 if self.retail_price else None,
            'theme': self.theme.name
        }

    @classmethod
    def find_by_set_num(cls, set_num):
        return cls.query.filter(cls.set_num == set_num).first()

    @classmethod
    def find_all_by_eol(cls, eol):
        return cls.query.filter(cls.eol == eol).all()
