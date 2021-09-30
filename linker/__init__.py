from flask import Flask, request
from .application import Application
import os
from . import db

application = Application()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'linker.sqlite'),
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.add_url_rule('/', 'home', application.home)

    db.init_app(app)

    app.register_blueprint(application.account.bp)
    app.register_blueprint(application.links.bp)

    return app