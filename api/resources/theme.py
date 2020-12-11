from flask import Blueprint, jsonify
from flask_restful import Resource

from db import db

from models.theme import ThemeModel

theme_bp = Blueprint('order_api', __name__)


class Theme(Resource):
    def get(self, id):
        pass


def getThemes(node):
    if len(node.children) == 0:
        return {'id': node.id,
                'name': node.name,
                'parent': node.parent_id,
                'children': []
                }
    else:
        return {'id': node.id,
                'name': node.name,
                'parent': node.parent_id,
                'children': list(map(lambda x: getThemes(x), node.children))}


@theme_bp.route('/api/themes/hierarchy')
def themesHierarchy():
    parent_themes = db.session.query(
        ThemeModel
    ).filter(ThemeModel.parent_id == None).all()
    return jsonify([getThemes(t) for t in parent_themes])
