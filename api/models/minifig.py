from sqlalchemy import (
    Boolean,
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
    rebrickable_id = Column(Integer)
    has_unique_part = Column(Boolean)
    year_of_publication = Column(Integer)
    is_minidoll = Column(Boolean, nullable=False, server_default='f')
    unique_character = Column(Boolean, nullable=False, server_default='f')
