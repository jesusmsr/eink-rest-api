from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from datetime import timedelta

db = SQLAlchemy()
load_dotenv()

def create_app():
    app = Flask(__name__)
    migrate = Migrate(app, db)

    CORS(
        app,
        origins="https://app.jsanr.dev",
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
        expose_headers=["Authorization"],  # <-- Expone Authorization
        allow_headers=["Content-Type", "Authorization"]  # <-- Permite Authorization
    )
    app.config['UPLOAD_FOLDER'] = os.path.join('app', 'static', 'images')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.bmp']
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

    db.init_app(app)
    jwt = JWTManager(app)

    from .routes import routes
    app.register_blueprint(routes)

    with app.app_context():
        db.create_all()

    return app
