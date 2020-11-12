from flask import Flask
from flask_restful import Api

from db import db

from resources.color import Color
from resources.element import Element
from resources.inventory import Inventory
from resources.minifig import Minifig
from resources.part import Part
from resources.score import Score
from resources.set import Set, SetList
from resources.theme import Theme


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rebrickable_new.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'brick_eval'
api = Api(app)

api.add_resource(Color, '/color/<int:_id>')
api.add_resource(Set, '/set/<string:set_num>')
api.add_resource(SetList, '/sets/<string:eol>')
api.add_resource(Score, '/score/<int:id>')


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)
