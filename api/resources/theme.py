from flask_restful import Resource

from models.theme import ThemeModel


class Theme(Resource):
    def get(self, id):
        pass
