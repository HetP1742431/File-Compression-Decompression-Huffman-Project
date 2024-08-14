from flask import Flask
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler


def create_app():
    app = Flask(__name__)

    load_dotenv()

    app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

    from .routes import main
    app.register_blueprint(main)

    # Configure logging
    if not app.debug:
        file_handler = RotatingFileHandler(
            'error.log', maxBytes=10240, backupCount=10)
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)

    return app
