"""Routes for habit tracker."""

from flask import Flask, render_template, redirect, flash, request, session
from flask_debugtoolbar import DebugToolbarExtension
from datetime import datetime, timedelta
import requests
from pytemperature import k2f
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

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
@app.route("/new")
def show_add_new_form():
    """Show the page where you can create a new Habit, Influence, or Symptom."""

    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.get(user_id)
        return render_template("new.html", habits=user.habits,
                               influences=user.influences,
                               symptoms=user.symptoms)
    else:
        redirect("/login")


@app.route("/new", methods=["POST"])
def add_new_event_type():
    """Instantiate a new Habit, Influence, or Symptom."""

    event_type = request.form.get("eventType")
    label = request.form.get("label")
    unit = request.form.get("unit")

    user_id = session["user_id"]
    user = User.query.get(user_id)

    if event_type == "habit":
        labels = [habit.label for habit in user.habits]
        new_event = Habit(label=label, unit=unit, user_id=user_id)
    elif event_type == "influence":
        labels = [influence.label for influence in user.influences]
        new_event = Influence(label=label, scale=unit, user_id=user_id)
    elif event_type == "symptom":
        labels = [symptom.label for symptom in user.symptoms]
        new_event = Symptom(label=label, scale=unit, user_id=user_id)

    if label not in labels:
        db.session.add(new_event)
        db.session.commit()
        return f"New {event_type} added successfully!"
    else:
        return f"You already have a(n) {event_type} with that title." 


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
    """Track user's current weather & temp info."""
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

    weather_id = weather_info['weather'][0]['id']
    weather_infl = Influence.query.filter_by(label='weather').one()
    weather_event = InfluenceEvent(user_id=user_id, influence_id=weather_infl.id,
                                   intensity=weather_id, timestamp=timestamp,
                                   latitude=lat, longitude=lon)

    db.session.add(temp_event)
    db.session.add(weather_event)
    db.session.commit()


def enable_gcal():
    """Have user authenticate GCal, or verify they already have."""

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

@app.route("/track-gcal-habits", methods=["POST"])
def get_events():
    """Gets events with `keyword` in title and tracks them as `habit_id`."""

    service = enable_gcal()

    dt_start = (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z'
    dt_end = datetime.utcnow().isoformat() + 'Z'

    calendars = service.calendarList().list().execute()['items']
    events = []
    
    for calendar in calendars:
        events_result = service.events().list(calendarId=calendar['id'],
                                        timeMin=dt_start, timeMax=dt_end,
                                        singleEvents=True,
                                        orderBy='startTime').execute()
        events += events_result["items"]

    user = User.query.get(session["user_id"])
    habits = user.habits

    events_tracked = ""
    # if any events have habit labels in the title, track them as habit events
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        title = event['summary'].lower()
        title_words = title.split()
        for habit in habits:
            if habit.label.lower() in title_words:
                habit_event = HabitEvent(user_id=user.id,
                                         habit_id=habit.id, 
                                         num_units=1, timestamp=start)
                # later: get lat & lon from gcal event location
                                #,latitude=latitude, longitude=longitude)
                # prevent duplicates
                old_habits = db.session.query(HabitEvent)
                duplicate = old_habits.filter(HabitEvent.user_id == habit_event.user_id,
                                HabitEvent.timestamp == habit_event.timestamp,
                                HabitEvent.habit_id == habit_event.habit_id).all()
                if not duplicate:
                    db.session.add(habit_event)
                    events_tracked += f"Habit: {habit.label}, Event: {title} {start}\n"

    db.session.commit()

    return events_tracked



# add a route to view your data



if __name__ == "__main__":
    app.debug = True
    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')