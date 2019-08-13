"""Routes for habit tracker."""

from flask import Flask, render_template, redirect, flash, request, session
from flask_debugtoolbar import DebugToolbarExtension

from models import *

app = Flask(__name__)

app.secret_key = "lajosjfikhafbajhbdfka"


def connect_to_db(app):
    """Connect Flask app to habit-tracker database."""

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///habit-tracker"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


@app.route("/")
def show_homepage():
    """Show homepage."""

    return render_template("index.html")


@app.route("/register")
def show_register_form():
    """Show registration page."""

    return render_template("register.html")


@app.route("/login")
def show_login_form():
    """Show login page."""

    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    """Log user into the session."""

    username = request.form.get('username')
    session['username'] = username

    flash("Login successful")

    return redirect("/")


@app.route("/register", methods=["POST"])
def register():
    """Instantiate a new User and log them into the session."""

    # instantiate new user

    flash("Registration successful")

    login()

    return redirect("/")


@app.route("/logout")
def log_out():
    """Removing user session data at logout."""
    
    session.clear()

    return redirect("/")









# logout
# fix register & login routes to actually interact with database
# add new habit/influence/symptom to track
# track habit event/influence event/symptom event
# view data










if __name__ == "__main__":
    app.debug = True
    DebugToolbarExtension(app)
    app.run(port=5000, host='0.0.0.0')

    connect_to_db(app)

    