from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Ensure upload directory exists
    upload_dir = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    db.init_app(app)
    
    from app.routes import bp as app_bp
    app.register_blueprint(app_bp)
    
    with app.app_context():
        db.create_all()
    
    return app
