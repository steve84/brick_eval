from flask_restful import Resource

from models.color import ColorModel
from schemas.color import ColorSchema


color_schema = ColorSchema()


class Color(Resource):
    def get(self, _id):
        color = ColorModel.find_by_id(_id)

        if color:
            return color_schema.dump(color)

        return {'message': 'Color not found.'}, 404
