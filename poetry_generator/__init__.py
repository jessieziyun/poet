from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app(config_file='settings.py'):
    app = Flask(__name__, static_url_path="/static", static_folder="static")
    app.config.from_pyfile(config_file)

    from .routes import generator
    app.register_blueprint(generator)
    
    socketio.init_app(app)
    return app