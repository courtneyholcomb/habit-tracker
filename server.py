"""Routes for habit tracker."""

from flask import Flask, render_template, redirect, flash, request, session
from flask_debugtoolbar import DebugToolbarExtension
from datetime import datetime
import requests
from pytemperature import k2f

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
    if "username" not in session:
        return redirect("/login")
    else:
        return redirect("/track")


@app.route("/login")
def show_login_form():
    """Show login page."""

    return render_template("login.html")


@app.route("/validate-login", methods=["POST"])
def validate_login():
    """Check that username exists and password matches for that User."""

    username = request.form.get("username")
    password = request.form.get("password")

    users = db.session.query(User).all()
    usernames = [user.username for user in users]

    if username not in usernames:
        return "There is no account associated with that username."
    else:
        user = db.session.query(User).filter_by(username=username).one()

    if password != user.password:
        return "Incorrect password."
    else:
        return ""


@app.route("/login", methods=["POST"])
def login():
    """Log user into the session."""

    username = request.form.get("username")
    user = User.query.filter_by(username=username).one()


    session["username"] = username
    session["user_id"] = user.id

    flash("Login successful")

    return redirect("/track")


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

    return redirect("/track")


@app.route("/logout")
def log_out():
    """Removing user session data at logout."""
    
    session.clear()

    return redirect("/login")


# add something new you want to track
@app.route("/add-new")
def show_add_new_form():
    """Show the page where you can create a new Habit, Influence, or Symptom."""

    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.get(user_id)
        return render_template("add-new.html", habits=user.habits,
                               influences=user.influences,
                               symptoms=user.symptoms)
    else:
        redirect("/login")


@app.route("/new-habit", methods=["POST"])
def add_new_habit():
    """Instantiate a new Habit."""

    label = request.form.get("label")
    unit = request.form.get("unit")

    user_id = session["user_id"]
    user = User.query.get(user_id)

    habit_labels = [habit.label for habit in user.habits]

    if label not in habit_labels:
        new_habit = Habit(label=label, unit=unit, user_id=user_id)
        db.session.add(new_habit)
        db.session.commit()
        return "New habit added successfully."
    else:
        return "You already have a habit with that title." 


@app.route("/new-influence", methods=["POST"])
def add_new_influence():
    """Instantiate a new Influence."""

    label = request.form.get("label")
    scale = request.form.get("scale")

    user_id = session["user_id"]
    user = User.query.get(user_id)

    influence_labels = [influence.label for influence in user.influences]

    if label not in influence_labels:
        new_influence = Influence(label=label, scale=scale, user_id=user_id)
        db.session.add(new_influence)
        db.session.commit()
        return "New influence added successfully."
    else:
        return "You already have an influence with that title."


@app.route("/new-symptom", methods=["POST"])
def add_new_symptom():
    """Instantiate a new Symptom."""

    label = request.form.get("label")
    scale = request.form.get("scale")

    user_id = session["user_id"]
    user = User.query.get(user_id)

    symptom_labels = [symptom.label for symptom in user.symptoms]

    if label not in symptom_labels:
        new_symptom = Symptom(label=label, scale=scale, user_id=user_id)
        db.session.add(new_symptom)
        db.session.commit()
        return "New symptom added successfully."
    else:
        return "You already have a symptom with that title."


# track something
@app.route("/track")
def show_track_page():
    """Show the page where you can track a Habit, Influence, or Symptom."""
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.get(user_id)
        return render_template("track.html", habits=user.habits,
                               influences=user.influences,
                               symptoms=user.symptoms)
    else:
        redirect("/login")


@app.route("/add-habit-event", methods=["POST"])
def track_habit():
    """Instantiate a new HabitEvent."""

    user_id = session["user_id"]
    num_units = request.form.get("num_units")

    habit_id = request.form.get("habit")
    habit = Habit.query.get(habit_id)

    # if the user entered a datetime, use that. if not, use current time.
    time_input = request.form.get("datetime")
    if time_input:
        timestamp = datetime.fromisoformat(time_input)
    else:
        timestamp = datetime.now()

    location = request.form.get("location")
    latitude = None
    longitude = None

    if location:
        coords = location.split(",")
        latitude = float(coords[0])
        longitude = float(coords[1])
        track_current_weather(latitude, longitude)

    new_habit_event = HabitEvent(user_id=user_id, habit_id=habit_id, 
                                 num_units=num_units, timestamp=timestamp,
                                 latitude=latitude, longitude=longitude)
    db.session.add(new_habit_event)
    db.session.commit()

    return "Habit tracked successfully!"


@app.route("/add-influence-event", methods=["POST"])
def track_influence():
    """Instantiate a new InfluenceEvent."""

    user_id = session["user_id"]
    intensity = request.form.get("intensity")

    influence_id = request.form.get("influence")
    influence = Influence.query.get(influence_id)

    # if the user entered a datetime, use that. if not, use current time.
    time_input = request.form.get("datetime")
    if time_input:
        timestamp = datetime.fromisoformat(time_input)
    else:
        timestamp = datetime.now()

    location = request.form.get("location")

    latitude = None
    longitude = None

    if location:
        coords = location.split(",")
        latitude = float(coords[0])
        longitude = float(coords[1])
        track_current_weather(latitude, longitude)

    new_influence_event = InfluenceEvent(user_id=user_id,
                                         influence_id=influence_id, 
                                         intensity=intensity,
                                         timestamp=timestamp, latitude=latitude,
                                         longitude=longitude)
    db.session.add(new_influence_event)
    db.session.commit()

    return "Influence tracked successfully!"


@app.route("/add-symptom-event", methods=["POST"])
def track_symptom():
    """Instantiate a new SymptomEvent."""

    user_id = session["user_id"]
    intensity = request.form.get("intensity")

    symptom_id = request.form.get("symptom")
    symptom = Symptom.query.get(symptom_id)

    # if the user entered a datetime, use that. if not, use current time.
    time_input = request.form.get("datetime")
    if time_input:
        timestamp = datetime.fromisoformat(time_input)
    else:
        timestamp = datetime.now()

    location = request.form.get("location")
    latitude = None
    longitude = None

    if location:
        coords = location.split(",")
        latitude = float(coords[0])
        longitude = float(coords[1])
        track_current_weather(latitude, longitude)

    new_symptom_event = SymptomEvent(user_id=user_id,
                                         symptom_id=symptom_id, 
                                         intensity=intensity,
                                         timestamp=timestamp, latitude=latitude,
                                         longitude=longitude)
    db.session.add(new_symptom_event)
    db.session.commit()

    return "Symptom tracked successfully!"


def track_current_weather(latitude, longitude):
    """Get weather info based on `datetime` and `location`."""
    lat = latitude
    lon = longitude

    response_obj = requests.get(f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&APPID=d5dffb69aad97a8a136ece32fe31a774")

    weather_info = response_obj.json()

    temp_info = weather_info['main']
    current_temp_f = k2f(temp_info['temp'])

    user_id = session["user_id"]
    timestamp = datetime.now()
    

    temp_infl = Influence.query.filter_by(label="temperature").one()
    temp_event = InfluenceEvent(user_id=user_id, influence_id=temp_infl.id,
                                intensity=current_temp_f, timestamp=timestamp,
                                latitude=lat, longitude=lon)

    db.session.add(temp_event)
    db.session.commit()
    
    # diff influence for each type of weather? or make intensity column more flexible/able to take a string?
    # figure out what all possible weather options are and make a diff influence for each?
    # weather_detail = weather_info['weather']['main']
    # weather_infl = Influence.query.filter_by(label=???)
    # weather_event = InfluenceEvent(user_id=user_id, influence_id=weather_inf.id,
    #                                intensity=???, timestamp=timestamp,
    #                                latitude=lat, longitude=lon)



# add a route to view your data



if __name__ == "__main__":
    app.debug = True
    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')