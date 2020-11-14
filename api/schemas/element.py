from ma import ma
from models.element import ElementModel
from schemas.color import ColorSchema
from schemas.part import PartSchema


class ElementSchema(ma.SQLAlchemyAutoSchema):
    color = ma.Nested(ColorSchema)
    part = ma.Nested(PartSchema)

    class Meta:
        model = ElementModel
        load_instance = True
        include_fk = True
