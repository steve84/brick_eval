from ma import ma
from models.set import SetModel
from schemas.theme import ThemeSchema


class SetSchema(ma.SQLAlchemyAutoSchema):
    theme = ma.Nested(ThemeSchema)

    class Meta:
        model = SetModel
        load_instance = True
        include_fk = True
