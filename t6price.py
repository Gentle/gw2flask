from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

from gw2spidy import Gw2Spidy

t6price = Blueprint('t6price', __name__,
                    template_folder='templates')

def pretty_money(value):
    value = str(value)
    value = value.split('.')[0]
    result = "%sc" % (value[-2:])
    if len(value) > 2:
        value = value[:-2]
    else:
        return result
    result = "%ss%s" % (value[-2:], result)
    if len(value) > 2:
        value = value[:-2]
    else:
        return result
    return "%sg%s" % (value, result)

@t6price.route('/')
def view():
    ids = [24358,
           24289,
           24300,
           24277,
           24283,
           24295,
           24351,
           24357,
    ]
    items = []
    for item_id in ids:
        data = Gw2Spidy.getItemData(item_id)
        items.append(data)
    return render_template('t6price.html', items=items, pretty_money=pretty_money)
