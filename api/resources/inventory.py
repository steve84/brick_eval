from flask_restful import Resource

from models.inventory import (
    InventoryModel,
    InventoryPartModel,
    InventoryMinifigModel,
    InventorySetModel
)


class Inventory(Resource):
    def get(self, id):
        pass
