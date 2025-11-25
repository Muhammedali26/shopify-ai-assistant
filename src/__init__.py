from flask import Flask
from flask_cors import CORS
from src.routes import main_bp

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    app.register_blueprint(main_bp)
    return app
