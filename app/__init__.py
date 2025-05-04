from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

db = SQLAlchemy()
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, origins="https://app.jsanr.dev") 
    app.config['UPLOAD_FOLDER'] = os.path.join('app', 'static', 'images')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.bmp']

    db.init_app(app)

    from .routes import routes
    app.register_blueprint(routes)

    with app.app_context():
        db.create_all()

    return app
