from flask_restful import Resource

from models.color import ColorModel


class Color(Resource):
    def get(self, _id):
        color = ColorModel.find_by_id(_id)

        if color:
            return color.json()

        return {'message': 'Color not found.'}, 404
