import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from models import db
from dotenv import load_dotenv
from flask_login import LoginManager
from datetime import timedelta
#from config import Config
#from routes.product import product_bp
#from routes.order import order_bp
#from routes.cart import cart_bp

mail = Mail()
jwt = JWTManager()


# Create Flask app
def create_app(*args, **kwargs):
    app = Flask(__name__)

    
    # Initialize CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],  
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
        }
    })
    
    # Load environment variables from .env file if running locally
    if os.getenv("RAILWAY_ENV") is None:  # Railway automatically injects its env vars
        load_dotenv()
    
    #app.config.from_object(Config)
    db_connect = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_connect

    mail_user=os.environ.get("MAIL_USERNAME","test@email.com")
    app.config["MAIL_USERNAME"] = mail_user

    mail_pass=os.environ.get("MAIL_PASSWORD","yourpassword")
    app.config["MAIL_PASSWORD"] = mail_pass

    mail_defsender=os.environ.get("MAIL_DEFAULT_SENDER","test@email.com")
    app.config["MAIL_DEFAULT_SENDER"] = mail_defsender

    sql_track=os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS","False")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = sql_track

    jwt_secret=os.environ.get("JWT_SECRET_KEY","secret")
    app.config["JWT_SECRET_KEY"] = jwt_secret
    
    mail_port=os.environ.get("MAIL_PORT","587")
    app.config["MAIL_PORT"] = mail_port

    mail_user_tls=os.environ.get("MAIL_USE_TLS","True")
    app.config["MAIL_USE_TLS"] = mail_user_tls

    mail_server=os.environ.get("MAIL_SERVER")
    app.config["MAIL_SERVER"] = mail_server

    secret_key=os.environ.get("SECRET_KEY","yoursecretkey")
    app.config["SECRET_KEY"] = secret_key

    secure_pass_salt=os.environ.get("SECURITY_PASSWORD_SALT","yoursalt")
    app.config["SECURITY_PASSWORD_SALT"] = secure_pass_salt

    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)

    # Initialize Extensions
    db.init_app(app)
    Migrate(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    # Initialize flask_login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User  # Import here to avoid circular imports
        return User.query.get(int(user_id))

    from routes.auth import auth_bp
    from routes.home import home_bp
    from routes.cart import cart_bp
    from routes.product import product_bp
    from routes.group_buy import group_buy_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(home_bp, url_prefix="/")
    app.register_blueprint(product_bp, url_prefix="/api/products")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(group_buy_bp, url_prefix="/api/groupbuy")

    #Future Blueprints
    #app.register_blueprint(product_bp, url_prefix="/api/products")
    #app.register_blueprint(order_bp, url_prefix="/api/orders")

    # Error Handling
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found"}), 404
    
    
    return app

app = create_app()
