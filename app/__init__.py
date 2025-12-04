from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static',
                static_url_path='')
    
    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
    app.config['DEBUG'] = True
    
    # ImgBB API Configuration
    app.config['IMGBB_API_KEY'] = os.getenv('IMGBB_API_KEY')

    # Feature flags (tạm thời vô hiệu hóa thăng cấp, danh hiệu, huy hiệu)
    app.config['PROGRESSION_ENABLED'] = True  # Điểm, level, leaderboard, activities
    app.config['RANK_TITLES_ENABLED'] = True  # Danh hiệu cấp bậc
    app.config['BADGES_ENABLED'] = True       # Huy hiệu người dùng
    
    # Configure MySQL connection
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    app.config['MYSQL_DATABASE'] = os.getenv('MYSQL_DATABASE')
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CORS(app)
    
    # Import models and blueprints
    from .models.user import User
    from .routes.auth import auth
    from .routes.comic import comic
    from .routes.main import main
    from .routes.admin import admin
    from .routes.progression import progression_bp
    
    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(comic, url_prefix='/comics')
    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(progression_bp, url_prefix='/progression')
    
    # Setup login manager
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create database tables
    # with app.app_context():
    #     db.create_all()

    # Context processor to expose feature flags to all templates without using current_app
    @app.context_processor
    def inject_feature_flags():
        return {
            'PROGRESSION_ENABLED': app.config.get('PROGRESSION_ENABLED', True),
            'RANK_TITLES_ENABLED': app.config.get('RANK_TITLES_ENABLED', True),
            'BADGES_ENABLED': app.config.get('BADGES_ENABLED', True)
        }
    
    return app
