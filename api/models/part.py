from sqlalchemy import (
    Column,
    Integer,
    Text
)

from db import db


class PartCategoryModel(db.Model):
    __tablename__ = 'part_categories'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class PartRelationshipModel(db.Model):
    __tablename__ = 'part_relationships'
    __table_args__ = (
        db.UniqueConstraint('rel_type', 'child_part_id',
                            'parent_part_id', name='part_relationship_index'),
    )

    id = Column(Integer, primary_key=True)
    rel_type = Column(Text, nullable=False)
    child_part_id = Column(Integer, db.ForeignKey('parts.id'), nullable=False)
    parent_part_id = Column(Integer, db.ForeignKey('parts.id'), nullable=False)

    child_part = db.relationship('PartModel', foreign_keys=[child_part_id])
    parent_part = db.relationship('PartModel', foreign_keys=[parent_part_id])


class PartModel(db.Model):
    __tablename__ = 'parts'

    id = Column(Integer, primary_key=True)
    part_num = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    part_cat_id = Column(Integer,
                         db.ForeignKey('part_categories.id'),
                         nullable=False)
    part_material = Column(Text, nullable=False)

    part_category = db.relationship('PartCategoryModel')


class PartColorFrequencyModel(db.Model):
    __tablename__ = 'part_color_frequencies'
    __table_args__ = (
        db.UniqueConstraint(
            'color_id',
            'part_id',
            name='part_color_freq_index'),
    )

    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, db.ForeignKey('parts.id'), nullable=False)
    color_id = Column(Integer, db.ForeignKey('colors.id'), nullable=False)
    total_amount = Column(Integer, nullable=False, server_default='0')

    part = db.relationship('PartModel')
