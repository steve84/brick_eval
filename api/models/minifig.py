from sqlalchemy import (
    Column,
    Integer,
    Text
)

from db import db


class MinifigModel(db.Model):
    __tablename__ = 'minifigs'

    id = Column(Integer, primary_key=True)
    fig_num = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    num_parts = Column(Integer, nullable=False)
