"""Routes for habit tracker."""

import requests
import json
import os
from datetime import datetime, timedelta
import ipdb

from flask import Flask, render_template, redirect, flash, request, session, url_for
from flask_debugtoolbar import DebugToolbarExtension

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle


from models import *

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")


def connect_to_db(app):
    """Connect Flask app to habit-tracker database."""

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///habit-tracker"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


### basic routes to register, login, logout
@app.route("/")
def show_homepage():
    """Show homepage."""
    if "username" not in session:
        return redirect(url_for('show_login_form'))
    else:
        return redirect(url_for('show_track_page'))


@app.route("/login")
def show_login_form():
    """Show login page."""

    return render_template("login.html")


@app.route("/login", methods=["POST"])
def validate_login():
    """Validate username and password then log user in.."""

    username = request.form.get("username")
    password = request.form.get("password")

    try:
        user = db.session.query(User).filter(User.username == username,
                                             User.password == password).one()
        session["username"] = username
        session["user_id"] = user.id
        flash("Login successful")
        return "OK", 200
    except:
        return "Incorrect username or password."    


@app.route("/register")
def show_register_form():
    """Show registration page."""

    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    """Validate and instantiate a new User then log them into the session."""

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confpass = request.form.get("confpass")

    try:
        db.session.query(User).filter_by(email=email).one()
        return "There is already an account associated with that email."
    except:
        pass

    try:
        db.session.query(User).filter_by(username=username).one()
        return "Username already taken."
    except:
        pass

    if len(password) < 8:
        return "Password must be at least 8 characters."
    elif confpass != password:
        return "Passwords entered do not match."
    else:
        new_user = User(email=email, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful")

        validate_login()

        return "OK", 200


@app.route("/logout")
def log_out():
    """Removing user session data at logout."""
    
    session.clear()

    return redirect(url_for('show_login_form'))


### routes to add new things to track
@app.route("/new")
def show_add_new_form():
    """Show the page where you can create a new Habit, Influence, or Symptom."""

    if "user_id" in session:
        user = User.query.get(session["user_id"])
        return render_template("new.html", habits=user.habits,
                               influences=user.influences,
                               symptoms=user.symptoms)
    else:
        redirect(url_for('show_login_form'))


# @app.route("/get-user-info")
# def get_user_info():
#     """Get list of Habits, Influences, and Symptoms for logged in User."""

#     user = User.query.get(session["user_id"])
#     habits = [{"id": habit.id, "label": habit.label, "unit": habit.unit}
#              for habit in user.habits]
#     influences = [{"id": influence.id, "label": influence.label, 
#                  "scale": influence.scale} for influence in user.influences]
#     symptoms = [{"id": symptom.id, "label": symptom.label,
#                "scale": symptom.scale} for symptom in user.symptoms]

#     return json.dumps({"habits": habits, "influences": influences,
#             "symptoms": symptoms})


@app.route("/new", methods=["POST"])
def add_new_event_type():
    """Instantiate a new Habit, Influence, or Symptom."""

    event_type = request.form.get("eventType")
    label = request.form.get("label")
    unit = request.form.get("unit")

    user = User.query.get(session["user_id"])

    if event_type == "habit":
        labels = [habit.label for habit in user.habits]
        new_event_type = Habit(label=label, unit=unit, user_id=user.id)
    elif event_type == "influence":
        labels = [influence.label for influence in user.influences]
        new_event_type = Influence(label=label, scale=unit, user_id=user.id)
    elif event_type == "symptom":
        labels = [symptom.label for symptom in user.symptoms]
        new_event_type = Symptom(label=label, scale=unit, user_id=user.id)

    if label not in labels:
        db.session.add(new_event_type)
        db.session.commit()
        return f"New {event_type} added successfully!"
    else:
        return f"You already have a(n) {event_type} with that title." 


### routes to track something
@app.route("/track")
def show_track_page():
    """Show the page where you can track a Habit, Influence, or Symptom."""

    if "user_id" in session:
        user = User.query.get(session["user_id"])
        return render_template("track.html", habits=user.habits,
                               influences=user.influences,
                               symptoms=user.symptoms)
    else:
        return redirect(url_for('show_login_form'))


@app.route("/track", methods=["POST"])
def track_something():
    """Instantiate a new HabitEvent, InfluenceEvent, or SymptomEvent."""

    user_id = session["user_id"]
    num = request.form.get("num")

    event_type = request.form.get("eventType")
    type_id = request.form.get("typeId")

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

    if event_type == "habit":
        new_event = HabitEvent(user_id=user_id, habit_id=type_id, 
                                 num_units=num, timestamp=timestamp,
                                 latitude=latitude, longitude=longitude)
    elif event_type == "influence":
        new_event = InfluenceEvent(user_id=user_id, influence_id=type_id, 
                                   intensity=num, timestamp=timestamp,
                                   latitude=latitude, longitude=longitude)
    elif event_type == "symptom":
        new_event = SymptomEvent(user_id=user_id, symptom_id=type_id,
                                 intensity=num, timestamp=timestamp,
                                 latitude=latitude, longitude=longitude)
    db.session.add(new_event)
    db.session.commit()

    return f"{event_type.capitalize()} tracked successfully!"


def track_current_weather(latitude, longitude):
    """Track user's current weather & temp info."""
    lat = latitude
    lon = longitude

    weather_token = os.environ.get("WEATHER_TOKEN")
    response_obj = requests.get(f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&APPID={weather_token}")

    weather_info = response_obj.json()

    temp_info = weather_info['main']
    current_temp_f = 9 / 5 * (temp_info['temp'] - 273) + 32

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
    
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    user = User.query.get(session["user_id"])
    creds = user.gcal_token
    print(f"creds={creds}")

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials to db
        # with open(user.gcal_token, 'wb') as token:
        user.gcal_token = creds
        # with open('token.pickle', 'wb') as token:
        #     pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service


@app.route("/track-gcal-habits", methods=["POST"])
def get_events():
    """Track all past week's events with one of User's Habit labels in title."""

    service = enable_gcal()

    dt_start = request.form.get("startDate").datetime.isoformat() + 'Z'
    dt_end = request.form.get("endDate").datetime.isoformat() + 'Z'

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

### view your data
@app.route("/charts")
def show_charts_page():
    """Show page with User's charts."""

    return render_template("charts.html")


@app.route("/line1-events.json", methods=["POST"])
def get_events_for_line1():
    """Get specified events in JSON for line1 chart."""

    event_type = request.args.get("event_type")
    label = request.args.get("label")
    time_period = request.args.get("time_period")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    user = User.query.get(session["user_id"])

    if event_type == "habit":
        events = db.session.query(HabitEvent.datetime,
                 HabitEvent.num_units).filter(HabitEvent.user_id == user.id,
                 HabitEvent.datetime.between(start_time, end_time)).all()
    # elif event_type == "influence":
    #     events = user.influence_events
    # elif event_type == "symptom"
    #     events = user.symptom_events

    units_per_time = {}

    for event in events:
        units_per_time[event.datetime.date.day] = events.get(
            event.datetime.date.day, 0) + event.num_units

    sorted_units_per_time = sorted(units_per_time)

    keys = sorted_units_per_time.keys()
    values = sorted_units_per_time.values()

    return json.dumps({"keys": keys, "values": values})






if __name__ == "__main__":
    app.debug = True
    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')