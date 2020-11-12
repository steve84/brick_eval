from flask_restful import Resource

from models.set import SetModel


class Set(Resource):
    def get(self, set_num):
        set = SetModel.find_by_set_num(set_num)

        if set:
            return set.json()

        return {'message': 'Set not found.'}, 404


class SetList(Resource):
    def get(self, eol):
        sets = SetModel.find_all_by_eol(eol)

        if sets:
            return {'sets': [_set.json() for _set in sets]}

        return {'message': 'No sets found.'}, 404
