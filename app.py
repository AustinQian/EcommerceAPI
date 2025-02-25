from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from models import db
from routes.auth import auth_bp
import os

# Create Flask app
def create_app():
    app = Flask(__name__)

    # Load Configuration
    app.config.from_object("config.Config")

    # Initialize Extensions
    db.init_app(app)
    Migrate(app, db)
    jwt = JWTManager(app)

    # Register Routes
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Error Handling
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found"}), 404

    return app

# Run App
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
