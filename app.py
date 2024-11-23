from flask import Flask
from blueprints.search import bp as search_bp
app = Flask(__name__, static_url_path='/static', static_folder='static')


if __name__ == '__main__':
    app.register_blueprint(search_bp)
    app.run(debug=True)
