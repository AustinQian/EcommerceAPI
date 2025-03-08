from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from models import db
from config import Config
#from routes.product import product_bp
#from routes.order import order_bp
#from routes.cart import cart_bp

mail = Mail()
jwt = JWTManager()

# Create Flask app
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    Migrate(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    from routes.auth import auth_bp
    from routes.home import home_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(home_bp, url_prefix="/")

    #Future Blueprints
    #app.register_blueprint(product_bp, url_prefix="/api/products")
    #app.register_blueprint(order_bp, url_prefix="/api/orders")
    #app.register_blueprint(cart_bp, url_prefix="/api/cart")

    # Error Handling
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found"}), 404

    return app

# Run App
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
