from ma import ma
from models.part import PartModel, PartCategoryModel, PartRelationshipModel


class PartSchema(ma.SQLAlchemyAutoSchema):
    part_category = ma.Nested(PartCategorySchema)

    class Meta:
        model = PartModel
        load_instance = True
        include_fk = True


class PartCategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartCategoryModel
        load_instance = True


class PartRelationshipSchema(ma.SQLAlchemyAutoSchema):
    child_part = ma.Nested(PartSchema)
    parent_part = ma.Nested(PartSchema)

    class Meta:
        model = PartRelationshipModel
        load_instance = True
        include_fk = True
