from flask_restful import Resource

from models.element import ElementModel


class Element(Resource):
    def get(self, element_id):
        pass
