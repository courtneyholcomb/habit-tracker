"""Routes for habit tracker."""

from flask import Flask, render_template, redirect, flash, request, session
from flask_debugtoolbar import DebugToolbarExtension

from models import *

app = Flask(__name__)

app.secret_key = "lajosjfikhafbajhbdfka"


# database connection
def connect_to_db(app):
    """Connect Flask app to habit-tracker database."""

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///habit-tracker"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


# basic routes to register, login, logout
@app.route("/")
def show_homepage():
    """Show homepage."""

    return render_template("index.html")


@app.route("/register")
def show_register_form():
    """Show registration page."""

    users = db.session.query(User).all()
    usernames = [user.username for user in users]
    emails = [user.email for user in users]

    return render_template("register.html", usernames=usernames, emails=emails)


@app.route("/login")
def show_login_form():
    """Show login page."""

    usernames = db.session.query(User.username).all()

    return render_template("login.html", usernames=usernames)


@app.route("/login", methods=["POST"])
def login():
    """Log user into the session."""

    username = request.form.get("username")
    session["username"] = username

    flash("Login successful")

    return redirect("/")


@app.route("/register", methods=["POST"])
def register():
    """Instantiate a new User and log them into the session."""

    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")

    new_user = User(email=email, username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    flash("Registration successful")

    login()

    return redirect("/")


@app.route("/logout")
def log_out():
    """Removing user session data at logout."""
    
    session.clear()

    return redirect("/")


# add something new you want to track
@app.route("/add-new")
def show_add_new_form():
    """Show the page where you can create a new Habit, Influence, or Symptom."""

    return render_template("add-new.html")


@app.route("/new-habit", methods=["POST"])
def add_new_habit():
    """Instantiate a new Habit."""

    label = request.form.get("label")
    unit = request.form.get("unit")

    new_habit = Habit(label=label, unit=unit)
    db.session.add(new_habit)
    db.session.commit()

    return redirect("/add-new")


@app.route("/new-influence", methods=["POST"])
def add_new_influence():
    """Instantiate a new Influence."""

    label = request.form.get("label")
    unit = request.form.get("scale")

    new_influence = Influence(label=label, scale=scale)
    db.session.add(new_influence)
    db.session.commit()

    return redirect("/add-new")


@app.route("/new-symptom", methods=["POST"])
def add_new_symptom():
    """Instantiate a new Symptom."""

    label = request.form.get("label")
    unit = request.form.get("scale")

    new_symptom = Influence(label=label, scale=scale)
    db.session.add(new_symptom)
    db.session.commit()

    return redirect("/add-new")


# # track something
# @app.route("/track")
# """Show the page where you can track a Habit, Influence, or Symptom."""

#     return render_template("track.html")


# route to view data



if __name__ == "__main__":
    app.debug = True
    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')