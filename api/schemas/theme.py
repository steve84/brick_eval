from ma import ma
from models.theme import ThemeModel


class ThemeSchema(ma.SQLAlchemyAutoSchema):
    sub_theme = ma.Nested("self", many=True)

    class Meta:
        model = ThemeModel
        load_instance = True
        include_fk = True
