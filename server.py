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


@app.route("/login")
def show_login_form():
    """Show login page."""

    usernames = db.session.query(User.username).all()

    return render_template("login.html", usernames=usernames)


@app.route("/login", methods=["POST"])
def login():
    """Log user into the session."""

    username = request.form.get("username")
    user = User.query.filter_by(username=username).one()


    session["username"] = username
    session["user_id"] = user.user_id

    flash("Login successful")

    return redirect("/")


@app.route("/register")
def show_register_form():
    """Show registration page."""

    return render_template("register.html")


@app.route("/validate-registration", methods=["POST"])
def validate_registration():
    """Check that username/email are unique and password meets requirements."""

    users = db.session.query(User).all()
    usernames = [user.username for user in users]
    emails = [user.email for user in users]

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confpass = request.form.get("confpass")

    if email in emails:
        return "There is already an account associated with that email."
    elif username in usernames:
        return "Username already taken."
    elif len(password) < 8:
        return "Password must be at least 8 characters."
    elif confpass != password:
        return "Passwords entered do not match."
    else:
        return ""


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

    # check if habit is now in db; if so, flash success message

    return redirect("/add-new")


@app.route("/new-influence", methods=["POST"])
def add_new_influence():
    """Instantiate a new Influence."""

    label = request.form.get("label")
    unit = request.form.get("scale")

    new_influence = Influence(label=label, scale=scale)
    db.session.add(new_influence)
    db.session.commit()

    # check if habit is now in db; if so, flash success message

    return redirect("/add-new")


@app.route("/new-symptom", methods=["POST"])
def add_new_symptom():
    """Instantiate a new Symptom."""

    label = request.form.get("label")
    unit = request.form.get("scale")

    new_symptom = Influence(label=label, scale=scale)
    db.session.add(new_symptom)
    db.session.commit()

    # check if habit is now in db; if so, flash success message

    return redirect("/add-new")


# track something
@app.route("/track")
def show_track_page():
    """Show the page where you can track a Habit, Influence, or Symptom."""

    return render_template("track.html")


@app.route("/add-habit-event", methods=["POST"])
def track_habit():
    """Instantiate a new HabitEvent."""

    habit_label = request.form.get("label")
    habit = Habit.query.filter_by(label=habit_label).one()
    habit_id = habit.id

    user_id = session["user_id"]
    num_units = request.form.get("num_units")

    # if the user entered a datetime, use that. if not, use current time.
    timestamp = get(request.form.get("datetime"), now())

    # get location from browser?
    # only get location when something is tracked or track all the time?
    latitude = None
    longitude = None

    new_habit_event = HabitEvent(user_id=user_id, habit_id=habit_id, 
                                 num_units=num_units, timestamp=timestamp,
                                 latitude=latitude, longitude=longitude)
    db.session.add(new_habit_event)
    db.session.commit()

    return redirect("/track")


@app.route("/add-influence-event", methods=["POST"])
def track_influence():
    """Instantiate a new InfluenceEvent."""

    influence_label = request.form.get("label")
    influence = Influence.query.filter_by(label=influence_label).one()
    influence_id = influence.id

    user_id = session["user_id"]
    intensity = request.form.get("intensity")

    # if the user entered a datetime, use that. if not, use current time.
    timestamp = get(request.form.get("datetime"), now())

    latitude = None
    longitude = None

    new_influence_event = InfluenceEvent(user_id=user_id,
                                         influence_id=influence_id, 
                                         num_units=num_units,
                                         timestamp=timestamp, latitude=latitude,
                                         longitude=longitude)
    db.session.add(new_influence_event)
    db.session.commit()

    return redirect("/track")


@app.route("/add-symptom-event", methods=["POST"])
def track_symptom():
    """Instantiate a new SymptomEvent."""

    symptom_label = request.form.get("label")
    symptom = Symptom.query.filter_by(label=symptom_label).one()
    symptom_id = symptom.id

    user_id = session["user_id"]
    intensity = request.form.get("intensity")

    # if the user entered a datetime, use that. if not, use current time.
    timestamp = get(request.form.get("datetime"), now())

    latitude = None
    longitude = None

    new_symptom_event = SymptomEvent(user_id=user_id,
                                         symptom_id=symptom_id, 
                                         num_units=num_units,
                                         timestamp=timestamp, latitude=latitude,
                                         longitude=longitude)
    db.session.add(new_symptom_event)
    db.session.commit()

    return redirect("/track")



# add a route to view your data



if __name__ == "__main__":
    app.debug = True
    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')