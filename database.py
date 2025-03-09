#from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate
#import os
#
#db = SQLAlchemy()
#
#def create_app():
#    app = Flask(__name__)
#
#    # PostgreSQL Database Configuration
#    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
#        "DATABASE_URL", "postgresql://postgres:btVxwAkNCOWGYGueFDnVeIdERgDVJqOc@shinkansen.proxy.rlwy.net:31878/railway"
#    )
#    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
#    db.init_app(app)
#    migrate = Migrate(app, db)
#
#    return app
#
#app = create_app()
#
#if __name__ == "__main__":
#    app.run(debug=True)
#