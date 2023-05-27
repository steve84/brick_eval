from sqlalchemy import (
    Column,
    Boolean,
    Date,
    Float,
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
    name_de = Column(Text)
    year_of_publication = Column(Integer, nullable=False)
    theme_id = Column(Integer, db.ForeignKey('themes.id'), nullable=False)
    num_parts = Column(Integer, nullable=False)
    eol = Column(String(2), nullable=False, server_default='-1')
    has_stickers = Column(Boolean, nullable=False, server_default='f')
    score_id = Column(Integer, db.ForeignKey('scores.id'))
    root_theme_id = Column(Integer, db.ForeignKey('themes.id'))
    rebrickable_id = Column(Integer)
    lego_slug = Column(Text)

    theme = db.relationship('ThemeModel', foreign_keys=[theme_id])
    root_theme = db.relationship('ThemeModel', foreign_keys=[root_theme_id])
    score = db.relationship('ScoreModel')
    prices = db.relationship('SetPriceModel')



class SetPriceModel(db.Model):
    __tablename__ = 'set_prices'
    __table_args__ = (
        db.Index('set_price_index', 'set_id',
                 'check_date', unique=True),
    )

    id = Column(Integer, primary_key=True)
    retail_price = Column(Integer, nullable=False)
    check_date = Column(Date, nullable=False)
    set_id = Column(Integer, db.ForeignKey('sets.id'))


class VSetModel(db.Model):
    __tablename__ = 'v_sets'

    id = Column(Integer, primary_key=True)
    set_num = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    year_of_publication = Column(Integer, nullable=False)
    theme = Column(Text, nullable=False)
    theme_id = Column(Integer, nullable=False)
    root_theme = Column(Text, nullable=False)
    num_parts = Column(Integer, nullable=False)
    eol = Column(String(2))
    retail_price = Column(Integer)
    has_stickers = Column(Boolean, nullable=False)
    score = Column(Float)
