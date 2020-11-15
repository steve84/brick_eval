from flask import Flask
from flask_restless import APIManager

from db import db

from models.color import ColorModel
from models.element import ElementModel
from models.inventory import (
    InventoryModel,
    InventoryMinifigModel,
    InventoryPartModel,
    InventorySetModel
)
from models.minifig import MinifigModel
from models.part import PartModel
from models.score import ScoreModel
from models.set import SetModel
from models.theme import ThemeModel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rebrickable_new.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'brick_eval'


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    db.init_app(app)
    manager = APIManager(app, flask_sqlalchemy_db=db)
    manager.create_api(ColorModel)
    manager.create_api(ElementModel)
    manager.create_api(InventoryModel)
    manager.create_api(MinifigModel)
    manager.create_api(PartModel)
    manager.create_api(ScoreModel)
    manager.create_api(SetModel)
    manager.create_api(ThemeModel)
    app.run(port=5000, debug=True)
