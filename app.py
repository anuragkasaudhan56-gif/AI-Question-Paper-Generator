from flask import Flask, redirect, url_for
from flask_login import LoginManager

from config import Config
from models import db
from models.user import User

# Import Blueprints
from routes.auth import auth
from routes.dashboard import dashboard
from routes.generate import generate
from routes.history import history
from routes.download import download


# ==========================================
# CREATE FLASK APP
# ==========================================

app = Flask(__name__)

app.config.from_object(Config)


# ==========================================
# INITIALIZE DATABASE
# ==========================================

db.init_app(app)


# ==========================================
# LOGIN MANAGER
# ==========================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


# ==========================================
# REGISTER BLUEPRINTS
# ==========================================

app.register_blueprint(auth)

app.register_blueprint(dashboard)

app.register_blueprint(generate)

app.register_blueprint(history)

app.register_blueprint(download)


# ==========================================
# HOME ROUTE
# ==========================================

@app.route("/")
def home():

    return redirect(url_for("auth.login"))


# ==========================================
# CREATE DATABASE TABLES
# ==========================================

with app.app_context():

    db.create_all()


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )