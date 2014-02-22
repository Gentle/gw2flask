import os, sys

# the path to the bundled libraries
sys.path.insert(0,os.path.join(os.path.dirname(__file__), 'libs'))

from app import create_app

application = create_app()

if __name__ == '__main__':
    application.run(debug=True)
