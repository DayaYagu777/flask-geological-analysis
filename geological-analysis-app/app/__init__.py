from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Try to import FastAPI for modern features
try:
    from app.api_modern import create_fastapi_app
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    print("FastAPI not available - using Flask only")

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Ensure upload directory exists
    upload_dir = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'app.login'
    
    # User loader callback
    from app.models import get_user
    
    @login_manager.user_loader
    def load_user(user_id):
        return get_user(user_id)
    
    # Register Flask blueprints
    from app.routes import bp as app_bp
    app.register_blueprint(app_bp)
    
    # Add FastAPI integration if available
    if HAS_FASTAPI:
        try:
            # Mount FastAPI app for modern API endpoints
            from werkzeug.middleware.dispatcher import DispatcherMiddleware
            from werkzeug.serving import run_simple
            
            fastapi_app = create_fastapi_app()
            
            # Create dispatcher to handle both Flask and FastAPI
            app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
                '/api/v2': fastapi_app
            })
            
            print("✓ FastAPI integration enabled - modern API available at /api/v2/*")
            
        except Exception as e:
            print(f"FastAPI integration failed: {e}")
            print("Continuing with Flask-only mode")
    
    with app.app_context():
        db.create_all()
    
    return app

def run_hybrid_server(host='0.0.0.0', port=5000, debug=True):
    """
    Run the application with hybrid Flask+FastAPI support.
    """
    app = create_app()
    
    if HAS_FASTAPI and debug:
        print("\n" + "="*50)
        print("🚀 ENHANCED GEOLOGICAL ANALYSIS SERVER")
        print("="*50)
        print(f"📊 Flask Frontend: http://{host}:{port}")
        print(f"🔬 Traditional API: http://{host}:{port}/api/*")
        if HAS_FASTAPI:
            print(f"🌟 Modern API: http://{host}:{port}/api/v2/*") 
            print(f"📖 API Docs: http://{host}:{port}/api/v2/docs")
        print("="*50)
        print("Features:")
        print("  ✓ Geological data analysis (RMR, fractures)")
        print("  ✓ Advanced image processing")
        print("  ✓ Interactive stereonet visualization")
        print("  ✓ Enhanced statistical analysis")
        if HAS_FASTAPI:
            print("  ✓ Async API endpoints")
            print("  ✓ Automatic data validation") 
            print("  ✓ OpenAPI documentation")
        print("="*50 + "\n")
    
    app.run(host=host, port=port, debug=debug)
