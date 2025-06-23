from flask import Flask, url_for, redirect, flash, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Load from the root directory of your project (outside website/)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


# Initialize extensions globally
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Enable Flask-Bootstrap
    bootstrap = Bootstrap(app)

    # Flask app config
    app.debug = True
    app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")
    app.config['STRIPE_PUBLIC_KEY'] = os.getenv("STRIPE_PUBLIC_KEY")
    app.config['STRIPE_SECRET_KEY'] = os.getenv("STRIPE_SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sitedata.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize DB and Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Setup login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from . import views
    app.register_blueprint(views.main)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import events
    app.register_blueprint(events.bp)

    from . import payment
    app.register_blueprint(payment.bp)

    # Error handler for 404
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app
