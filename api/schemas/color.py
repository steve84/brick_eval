from ma import ma
from models.color import ColorModel


class ColorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ColorModel
        load_instance = True
