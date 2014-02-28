#!/usr/bin/env python
from gevent import monkey
monkey.patch_all()

import os
import sys

# the path to the bundled libraries
sys.path.insert(0,os.path.join(os.path.dirname(__file__), 'libs'))

from flask.ext.script import Manager

from app import create_app

app = create_app()
manager = Manager(app)

@manager.command
def import_all():
    from importer import import_all
    import_all()

@manager.command
def get_rarities():
    from importer import items
    from collections import defaultdict
    rarities = defaultdict(lambda: 0)
    for item_id in items:
        rarity = items[item_id].dict.get('rarity')
        rarities[rarity] += 1
        print "%s %s" % (rarity, rarities[rarity])
    print rarities


@manager.command
def migrate_redis():
    from redistypes import migrate
    migrate(('gw2', 'items'))
    migrate(('gw2', 'recipes'))

@manager.command
def dump_json():
    from importer import items, recipes
    import json

    def dump(name, stuff):
        data = []
        size = len(stuff)
        print "dumping %s" % (name)
        for (i, key) in enumerate(stuff, start=1):
            print "%s/%s" % (i, size)
            data.append(stuff[key].dict)
        path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(path, 'data')
        path = os.path.join(path, '%s.json' % (name))
        with open(path, 'w') as f:
            f.write(json.dumps(data))

    dump('items', items)
    dump('recipes', recipes)
    print __file__

if __name__ == "__main__":
    manager.run()
