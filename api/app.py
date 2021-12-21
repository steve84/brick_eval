from flask import Flask
from flask_restless import APIManager

from db import app, db

from models.set import SetModel, VSetModel
from models.color import ColorModel
from models.element import ElementPriceModel, PartColorFrequencyElementRelation
from models.inventory import (
    InventoryMinifigModel,
    MinifigInventoryRelation,
    SetInventoryRelation,
    InventoryModel,
    InventoryPartModel,
    InventorySetModel,
    VInventoryPartModel
)
from models.minifig import MinifigModel
from models.part import (
    PartCategoryModel,
    PartModel,
    PartColorFrequencyModel,
    PartRelationshipModel
)
from models.score import ScoreModel
from models.statistic import StatisticModel
from models.theme import ThemeModel

from resources.theme import theme_bp


# Do only create real tables (not views)
CREATE_TABLES = [
    SetModel.__table__,
    ColorModel.__table__,
    PartCategoryModel.__table__,
    PartColorFrequencyElementRelation.__table__,
    PartRelationshipModel.__table__,
    InventoryMinifigModel.__table__,
    MinifigInventoryRelation.__table__,
    SetInventoryRelation.__table__,
    InventoryModel.__table__,
    InventoryPartModel.__table__,
    InventorySetModel.__table__,
    MinifigModel.__table__,
    PartModel.__table__,
    PartColorFrequencyModel.__table__,
    ScoreModel.__table__,
    StatisticModel.__table__,
    ThemeModel.__table__,
    ElementPriceModel.__table__
]

@app.before_first_request
def create_tables():
    db.metadata.create_all(bind=db.engine, tables=CREATE_TABLES)


if __name__ == '__main__':
    manager = APIManager(app, session=db.session)
    manager.create_api(ColorModel, methods=['GET'])
    manager.create_api(ElementPriceModel, methods=['GET'])
    manager.create_api(InventoryModel, methods=['GET'])
    manager.create_api(InventoryMinifigModel, methods=['GET'])
    manager.create_api(InventoryPartModel, methods=['GET'])
    manager.create_api(VInventoryPartModel, methods=['GET'])
    manager.create_api(MinifigModel, methods=['GET'])
    manager.create_api(PartModel, methods=['GET'])
    manager.create_api(PartColorFrequencyElementRelation, methods=['GET'])
    manager.create_api(PartColorFrequencyModel, methods=['GET'])
    manager.create_api(ScoreModel, methods=['GET'])
    manager.create_api(SetModel, methods=['GET'])
    manager.create_api(VSetModel, methods=['GET'])
    manager.create_api(StatisticModel, methods=['GET'])
    manager.create_api(ThemeModel, methods=['GET'])
    manager.create_api(MinifigInventoryRelation, methods=[])
    manager.create_api(InventorySetModel, methods=[])
    manager.app.register_blueprint(theme_bp)
    app.run(port=5000, host='0.0.0.0', debug=True)
