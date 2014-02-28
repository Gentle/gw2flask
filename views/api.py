from flask import Blueprint, Response
from jinja2 import TemplateNotFound
import json

api = Blueprint('api', __name__,
                template_folder='templates')

from importer import items


@api.route('/items.json')
def items_all():
    def generate():
        yield "["
        for item_id in items:
            item = items[item_id].dict
            print item.get('name')
            yield "\n%s," % (json.dumps(item),)
        yield "]"

    return Response(generate(), mimetype='application/json')
