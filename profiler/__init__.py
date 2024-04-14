from flask import Flask
from flask import Blueprint

def create_app():
    app = Flask(__name__)

    app.config.from_pyfile("config.py", silent=True)
    from . import db
    db.init_app(app)
    
    from . import items
    app.register_blueprint(items.blueprint)

    

    return app