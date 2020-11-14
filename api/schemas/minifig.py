from ma import ma
from models.minifig import MinifigModel


class MinifigSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MinifigModel
        load_instance = True
