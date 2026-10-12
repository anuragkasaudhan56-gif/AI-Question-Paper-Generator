from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

from models import db
from models.user import User

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if email already exists
        user = User.query.filter_by(email=email).first()

        if user:
            flash("Email already exists.", "danger")
            return redirect(url_for("auth.register"))

        # Hash password
        hashed_password = generate_password_hash(password)

        # Create new user
        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            # ✅ Correct redirect
            return redirect(url_for("dashboard.dashboard_home"))

        flash("Invalid Email or Password", "danger")

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))