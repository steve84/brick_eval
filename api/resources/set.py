from flask_restful import Resource

from models.set import SetModel
from schemas.set import SetSchema


set_schema = SetSchema()
set_list_schema = SetSchema(many=True)


class Set(Resource):
    def get(self, set_num):
        set = SetModel.find_by_set_num(set_num)

        if set:
            return set_schema.dump(set)

        return {'message': 'Set not found.'}, 404


class SetList(Resource):
    def get(self, eol):
        sets = SetModel.find_all_by_eol(eol)

        if sets:
            return {'sets': set_list_schema.dump(sets)}

        return {'message': 'No sets found.'}, 404
