# coding: utf-8
from sqlalchemy import BigInteger, Boolean, Column, Integer, Float, String, Text, Table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Score(Base):
    __tablename__ = 'scores'

    inventory_id = Column(Integer, primary_key=True, nullable=False)
    inventory_type = Column(String(1), primary_key=True, nullable=False)
    inventory_number = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    needs_recalc = Column(Boolean, nullable=False)


class Property(Base):
    __tablename__ = 'properties'

    id = Column(Integer, primary_key=True, nullable=False)
    property_name = Column(Text, nullable=False)
    value = Column(Text, nullable=False)
    value_type = Column(Text, nullable=False)


class InventoryMinifigPartView(Base):
    __tablename__ = 'v_inventory_minifig_parts'

    inventory_id = Column(Integer, primary_key=True, nullable=False)
    part_num = Column(Text, primary_key=True, nullable=False)
    color_id = Column(Integer, primary_key=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_quantity = Column(Integer)


class InventoryPartView(Base):
    __tablename__ = 'v_inventory_parts'

    inventory_id = Column(Integer, primary_key=True, nullable=False)
    part_num = Column(Text, primary_key=True, nullable=False)
    color_id = Column(Integer, primary_key=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_quantity = Column(Integer)
