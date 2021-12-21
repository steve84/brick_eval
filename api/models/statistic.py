from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    Text,
    Float,
    Date
)

from db import db


class StatisticModel(db.Model):
    __tablename__ = 'statistics'

    id = Column(Integer, primary_key=True)
    is_set = Column(Boolean, nullable=False)
    theme_id = Column(Integer, db.ForeignKey('themes.id'))
    property_name = Column(Text, nullable=False)
    count = Column(Integer, nullable=False)
    mean = Column(Float, nullable=False)
    std = Column(Float, nullable=False)
    min_value = Column(Float, nullable=False)
    lower_quartil = Column(Float, nullable=False)
    median = Column(Float, nullable=False)
    upper_quartil = Column(Float, nullable=False)
    max_value = Column(Float, nullable=False)
    calc_date = Column(Date, nullable=False)

    theme = db.relationship('ThemeModel')
