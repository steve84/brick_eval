from flask_restful import Resource

from models.score import ScoreModel
from schemas.score import ScoreSchema


score_schema = ScoreSchema()


class Score(Resource):
    def get(self, _id):
        score = ScoreModel.find_by_id(_id)

        if score:
            return score_schema.dump(score)

        return {'message': 'No score found.'}, 404
