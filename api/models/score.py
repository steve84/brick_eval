from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    Date,
    Float,
    Text
)

from db import db


class ScoreModel(db.Model):
    __tablename__ = 'scores'

    id = Column(Integer, primary_key=True)
    inventory_id = Column(Integer,
                          db.ForeignKey('inventories.id'),
                          nullable=False)
    score = Column(Float, nullable=False)
    calc_date = Column(Date, nullable=False)

    inventory = db.relationship('InventoryModel',
                                lazy='subquery',
                                backref=db.backref('scores',
                                                   lazy=True))

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter(cls.inventory_id == _id).first()


class MinifigSimilarityModel(db.Model):
    __tablename__ = 'minifig_similarities'
    __table_args__ = (
        db.Index('minifig_similarity_index', 'inventory_minifig_id_1',
                 'inventory_minifig_id_2', unique=True),
    )

    id = Column(Integer, primary_key=True)
    inventory_minifig_id_1 = Column(Integer, db.ForeignKey('inventory_minifigs.id'), nullable=False)
    inventory_minifig_id_2 = Column(Integer, db.ForeignKey('inventory_minifigs.id'), nullable=False)
    set_occurance_minifig_1 = Column(Integer, nullable=False)
    set_occurance_minifig_2 = Column(Integer, nullable=False)
    max_set_parts_minifig_1 = Column(Integer, nullable=False)
    max_set_parts_minifig_2 = Column(Integer, nullable=False)
    min_set_parts_minifig_1 = Column(Integer, nullable=False)
    min_set_parts_minifig_2 = Column(Integer, nullable=False)
    score_minifig_1 = Column(Float, nullable=False)
    score_minifig_2 = Column(Float, nullable=False)
    num_parts_minifig_1 = Column(Integer, nullable=False)
    num_parts_minifig_2 = Column(Integer, nullable=False)
    theme_minifig_1 = Column(Text, nullable=False)
    theme_minifig_2 = Column(Text, nullable=False)
    name_minifig_1 = Column(Text, nullable=False)
    name_minifig_2 = Column(Text, nullable=False)
    num_minifig_1 = Column(Text, nullable=False)
    num_minifig_2 = Column(Text, nullable=False)
    rebrickable_id_minifig_1 = Column(Integer)
    rebrickable_id_minifig_2 = Column(Integer)
    year_of_publication_minifig_1 = Column(Integer, nullable=False)
    year_of_publication_minifig_2 = Column(Integer, nullable=False)
    similarity = Column(Float, nullable=False)



class VScoreModel(db.Model):
    __tablename__ = 'v_scores'

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    calc_date = Column(Date, nullable=False)
    is_set = Column(Boolean, nullable=False)
    num = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    year_of_publication = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)
    num_parts = Column(Integer, nullable=False)