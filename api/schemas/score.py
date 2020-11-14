from ma import ma
from models.score import ScoreModel


class ScoreSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ScoreModel
        load_instance = True
