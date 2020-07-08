from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_backend import config
import os

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = config.alchemy_uri()
    app.config['SQLALCHEMY_BINDS'] = config.bind_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
#    app.config["APPLICATION_ROOT"] = "/www/wsgi-scripts/tmcglynn/newgcn/"

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from flask_backend.models import db
    db.init_app(app)

    from flask_backend.views import public
    app.register_blueprint(public)

    return app