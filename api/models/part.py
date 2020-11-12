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

    def __init__(self, name):
        self.name = name


class PartRelationshipModel(db.Model):
    __tablename__ = 'part_relationships'
    __table_args__ = (
        db.UniqueConstraint('part_relationship_index', 'rel_type',
                            'child_part_id', 'parent_part_id', unique=True)
    )

    id = Column(Integer, primary_key=True)
    rel_type = Column(Text, nullable=False)
    child_part_id = Column(Integer, db.ForeignKey('parts.id'), nullable=False)
    parent_part_id = Column(Integer, db.ForeignKey('parts.id'), nullable=False)

    child_part = db.relationship('PartModel', foreign_keys=[child_part_id])
    parent_part = db.relationship('PartModel', foreign_keys=[parent_part_id])

    def __init__(self, rel_type, child_part_id, parent_part_id):
        self.rel_type = rel_type
        self.child_part_id = child_part_id
        self.parent_part_id = parent_part_id


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

    def __init__(self, part_num, name, part_cat_id, part_material):
        self.part_num = part_num
        self.name = name
        self.part_cat_id = part_cat_id
        self.part_material = part_material
