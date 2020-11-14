from ma import ma
from models.inventory import (
    InventoryModel, InventoryPartModel,
    InventoryMinifigModel, InventorySetModel)
from schemas.color import ColorSchema
from schemas.minifig import MinifigSchema
from schemas.part import PartSchema
from schemas.set import SetSchema


class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = InventoryModel
        load_instance = True
        include_fk = True


class InventoryPartSchema(ma.SQLAlchemyAutoSchema):
    color = ma.Nested(ColorSchema)
    part = ma.Nested(PartSchema)

    class Meta:
        model = InventoryPartModel
        load_instance = True
        include_fk = True


class InventoryMinifigSchema(ma.SQLAlchemyAutoSchema):
    minifig = ma.Nested(MinifigSchema)

    class Meta:
        model = InventoryMinifigModel
        load_instance = True
        include_fk = True


class InventorySetSchema(ma.SQLAlchemyAutoSchema):
    set = ma.Nested(SetSchema)

    class Meta:
        model = InventorySetModel
        load_instance = True
        include_fk = True
