from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # ================= CONFIG =================
    app.config.from_object("config.Config")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # SQLite database
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = '8c568937f79e5cc394a108a28ae6093d'

    # Ensure static folders exist
    os.makedirs(os.path.join("loan", "static", "reports"), exist_ok=True)
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
    # ==========================================

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    # Import and register blueprints
    from .routes import main
    app.register_blueprint(main)

    # ================= DATABASE =================
    # Create tables if they do not exist
    with app.app_context():
        db.create_all()
    # ============================================

    # Flask-Login user loader
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    return app
