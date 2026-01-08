from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# 1. Initialize extensions globally
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tradeguide.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 2. Init Extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login' # Points to the login route in routes.py

    # 3. THE MISSING PIECE: User Loader
    # We must import User here (inside function) to avoid circular import errors
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 4. Register Blueprints
    from app.routes import bp
    app.register_blueprint(bp)

    # 5. Create Database
    with app.app_context():
        db.create_all()

    return app