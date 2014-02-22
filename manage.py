#!/usr/bin/env python
from flask.ext.script import Manager

from app import create_app

app = create_app()
manager = Manager(app)

@manager.command
def import_all():
    from gevent import monkey
    monkey.patch_all()
    from importer import import_all
    import_all()

if __name__ == "__main__":
    manager.run()
