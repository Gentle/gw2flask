from flask import Flask, render_template
from t6price import t6price

app = Flask(__name__)

@app.route('/')
def index():
    sites = [{'name': "T6 prices", 'path': "t6price"},
    ]
    return render_template('index.html', sites=sites)

app.register_blueprint(t6price, url_prefix='/t6price')

if __name__ == '__main__':
    app.run(debug=True)
