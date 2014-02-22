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

if __name__ == "__main__":
    manager.run()
