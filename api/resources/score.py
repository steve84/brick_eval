from flask_restful import Resource

from models.score import ScoreModel


class Score(Resource):
    def get(self, id):
        score = ScoreModel.find_by_id(id)

        if score:
            return score.json()

        return {'message': 'No score found.'}, 404
