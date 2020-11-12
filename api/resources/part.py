from flask_restful import Resource

from models.part import (
    PartModel,
    PartCategoryModel,
    PartRelationshipModel
)


class Part(Resource):
    def get(self, id):
        pass
