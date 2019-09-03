"""Routes for habit tracker."""

import requests
import json
import os
from datetime import datetime, timedelta, date
from collections import defaultdict
import pickle
import pdb

from flask import Flask, render_template, redirect, flash, request, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from models import db, User, Habit, HabitEvent, Influence, InfluenceEvent, Symptom, SymptomEvent


app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")


def connect_to_db(app):
    """Connect Flask app to habit-tracker database."""

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///habit-tracker"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


### Routes to handle user registration, login, logout
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
        user = db.session.query(User).filter(User.username == username).one()

        if not bcrypt.check_password_hash(user.password, password):
            return "Incorrect username or password."

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

    ### Check that email & username are available
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

    ### Validate password
    if len(password) < 8:
        return "Password must be at least 8 characters."
    elif confpass != password:
        return "Passwords entered do not match."
    else:
        ### If all inputs are valid, create new user & log them in
        hash_pass = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(email=email, username=username, password=hash_pass)
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


def get_user():
    """Get user object from session."""

    if "user_id" in session:
        user = User.query.get(session["user_id"])
        return user


### Routes to add new things to track
@app.route("/new")
def show_add_new_form():
    """Show the page where you can create a new Habit, Influence, or Symptom."""

    if get_user():
        return render_template("new.html")

    else:
        redirect(url_for('show_login_form'))


@app.route("/user-event-types")
def get_user_event_types():
    """Get JSON of all Habits, Influences, and Symptoms for logged in User."""

    user = get_user()

    habits = [{"id": habit.id, "label": habit.label, "unit": habit.unit}
              for habit in Habit.query.filter_by(user_id=user.id).all()]
    influences = [{"id": infl.id, "label": infl.label, "scale": infl.scale}
                  for infl in Influence.query.filter_by(user_id=user.id).all()]
    symptoms = [{"id": symp.id, "label": symp.label, "scale": symp.scale}
                for symp in Symptom.query.filter_by(user_id=user.id).all()]

    return json.dumps({"habits": habits, "influences": influences,
        "symptoms": symptoms})


def validate_new_event_type(label):
    """Check if new event type label is already used by User."""

    user = get_user()

    try:
        if db.session.query(Habit).filter(Habit.label == label,
                                          Habit.user == user).all():
            return "You already have a habit with that title."
    except:
        pass

    try:
        if db.session.query(Influence).filter(Influence.label == label,
                                              Influence.user == user).all():
            return "You already have an influence with that title."
    except:
            pass

    try:
        if db.session.query(Symptom).filter(Symptom.label == label,
                                            Symptom.user == user).all():
            return "You already have a symptom with that title."
    except:
        return None


@app.route("/new", methods=["POST"])
def add_new_event_type():
    """Instantiate a new Habit, Influence, or Symptom."""

    event_type = request.form.get("eventType")
    label = request.form.get("label")
    unit = request.form.get("unit")

    user = get_user()

    invalid_message = validate_new_event_type(label)
    if invalid_message:
        return invalid_message
    
    if event_type == "habit":
        new_event_type = Habit(label=label, unit=unit, user_id=user.id)

    elif event_type == "influence":
        new_event_type = Influence(label=label, scale=unit, user_id=user.id)

    elif event_type == "symptom":
        new_event_type = Symptom(label=label, scale=unit, user_id=user.id)
    
    db.session.add(new_event_type)
    db.session.commit()

    return f"New {event_type} added successfully!"
        

### Routes to track events
@app.route("/track")
def show_track_page():
    """Show the page where you can track a Habit, Influence, or Symptom."""

    user = get_user()

    if user:
        return render_template("track.html")
    else:
        return redirect(url_for('show_login_form'))


def create_event(evt_type, user_id, type_id, num,
                 timestamp=datetime.now(), lat=None, lon=None):
    """Instantiate a new event."""

    user_id = session["user_id"]

    if evt_type == "habit":
        new_event = HabitEvent(user_id=user_id, habit_id=type_id, 
                                 num_units=num, timestamp=timestamp,
                                 latitude=lat, longitude=lon)
    elif evt_type == "influence":
        new_event = InfluenceEvent(user_id=user_id, influence_id=type_id, 
                                   intensity=num, timestamp=timestamp,
                                   latitude=lat, longitude=longitude)
    elif evt_type == "symptom":
        new_event = SymptomEvent(user_id=user_id, symptom_id=type_id,
                                 intensity=num, timestamp=timestamp,
                                 latitude=lat, longitude=lon)
    db.session.add(new_event)
    db.session.commit()


@app.route("/track", methods=["POST"])
def track_something():
    """Get inputs from tracking page and instantiate a new event."""

    user_id = session["user_id"]
    num = request.form.get("num")
    evt_type = request.form.get("eventType")
    type_id = request.form.get("typeId")
    location = request.form.get("location")
    lat = None
    lon = None
    pdb.set_trace()

    # If the user entered a datetime, use that. if not, use current time.
    time_input = request.form.get("datetime")
    if time_input:
        timestamp = datetime.fromisoformat(time_input)
    else:
        timestamp = datetime.now()

    # If user entered a location, track current weather.
    if location:
        lat, lon = location.split(",")
        track_current_weather(float(lat), float(lon))

    # Add the event to the db and return success message.
    create_event(evt_type, user_id, type_id, num, timestamp, lat, lon)
    return f"{evt_type.capitalize()} tracked successfully!"


def track_current_weather(lat, lon):
    """Track user's current weather & temp info."""

    user_id = session["user_id"]
    timestamp = datetime.now()

    # Get current weather from Open Weather API for given lat & lon
    weather_token = os.environ.get("WEATHER_TOKEN")
    response_obj = requests.get(f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&APPID={weather_token}")
    weather_info = response_obj.json()
    weather_id = weather_info['weather'][0]['id']

    temp_info = weather_info['main']
    current_temp_f = 9 / 5 * (temp_info['temp'] - 273) + 32

    temp_infl = ensure_tracking_infl("temperature", 125)
    weather_infl = ensure_tracking_infl("weather", 1000)

    # Add temp & weather events to db
    create_event("influence", user_id, temp_infl.id, current_temp_f,
                 timestamp, lat, lon)
    create_event("influence", user_id, weather_infl.id, weather_id, timestamp,
                 lat, lon)


def ensure_tracking_infl(label, scale):
    """If user doesn't track influence yet, add it."""

    try:
        return Influence.query.filter_by(label=label).one()

    except:
        new_infl = Influence(label=label, scale=scale, user_id=user_id)
        db.session.add(new_infl)
        db.session.commit()
        return new_infl


def enable_gcal():
    """Have user authenticate GCal, or verify they already have."""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    user = get_user()
    creds = user.gcal_token
    print(f"creds={creds}")

    # If no valid creds, prompt login.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials to db
        user.gcal_token = creds

    return build('calendar', 'v3', credentials=creds)


@app.route("/track-gcal-habits", methods=["POST"])
def get_gcal_events():
    """Track all past week's events with one of User's Habit labels in title."""

    user = get_user()
    dt_start = request.form.get("startDate")
    dt_end = request.form.get("endDate")
    habits = user.habits
    gcal_info = enable_gcal()

    if not dt_start:
        dt_start = (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z'
    if not dt_end:
        dt_end = datetime.utcnow().isoformat() + 'Z'

    calendars = gcal_info.calendarList().list().execute()['items']
    events = []
    
    for calendar in calendars:
        events_result = gcal_info.events().list(calendarId=calendar['id'],
                                        timeMin=dt_start, timeMax=dt_end,
                                        singleEvents=True,
                                        orderBy='startTime').execute()
        events += events_result["items"]

    # If any GCal events in time range have habit labels in title, track them.
    events_tracked = ""
    for event in events:
        # Get info from event
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        title = event['summary']
        title_words = set(title.lower().split())

        for habit in habits:
            if habit.label.lower() in title_words:

                # Check if event is already tracked
                duplicates = db.session.query(HabitEvent)\
                             .filter(HabitEvent.user_id == user.id,
                                     HabitEvent.timestamp == start,
                                     HabitEvent.habit_id == habit.id).all()

                if not duplicates:
                    create_event("habit", user.id, habit.id, 1, start)
                    events_tracked += f"Habit: {habit.label}, "\
                                      f"Event: {title} {start}\n"

    return events_tracked

### View your data + charts
@app.route("/charts")
def show_charts_page():
    """Show page with User's charts."""

    return render_template("charts.html")


def get_events_in_range(start, end):
    """Get all events that occurred during given date range for user."""

    user = get_user()

    habit_events = db.session.query(HabitEvent).filter(HabitEvent.timestamp
        .between(start, end), HabitEvent.user == user).all()

    influence_events = db.session.query(InfluenceEvent).filter(
        InfluenceEvent.timestamp.between(start, end),
        InfluenceEvent.user == user).all()

    symptom_events = db.session.query(SymptomEvent).filter(
        SymptomEvent.timestamp.between(start, end),
        SymptomEvent.user == user).all()

    return {"habit_events": habit_events, "influence_events": influence_events, 
            "symptom_events": symptom_events}

def get_evt_type_min_max(evt_type, label):
    """Get the min and max units for a user's events."""

    user = get_user()

    if evt_type == "habit":
        type_option = db.session.query(Habit).filter(Habit.user == user,
                                                    Habit.label == label).one()
        units = [evt.num_units for evt in type_option.habit_events]

    elif evt_type == "influence":
        type_option = db.session.query(Influence).filter(Influence.user == user,
                                                Influence.label == label).one()
        units = [evt.intensity for evt in type_option.influence_events]

    elif evt_type == "symptom":
        type_option = db.session.query(Symptom).filter(Symptom.user == user,
                                                Symptom.label == label).one()
        units = [evt.intensity for evt in type_option.symptom_events]

    return {"min": min(units), "max": max(units)}


def get_event_infos(start, end):
    """Reformat events info to be used later for line chart."""

    events_dict = get_events_in_range(start, end)
    habit_events = events_dict["habit_events"]
    influence_events = events_dict["influence_events"]
    symptom_events = events_dict["symptom_events"]


    habit_event_info = [(habit_event.habit, habit_event, habit_event.num_units,
                         "habit")
                         for habit_event in habit_events]

    influence_event_info = [(influence_event.influence, influence_event,
                             influence_event.intensity, "influence")
                            for influence_event in influence_events]
                            # if influence_event.influence.label 
                            #     not in ["weather", "temperature"]]

    symptom_event_info = [(symptom_event.symptom, symptom_event,
                           symptom_event.intensity, "symptom")
                          for symptom_event in symptom_events]

    event_infos = habit_event_info + influence_event_info + symptom_event_info

    return event_infos


@app.route("/line-chart-data", methods=["POST"])
def get_line_chart_data():
    """Get data needed for line chart."""

    start_input = request.form.get("startDate")
    end_input = request.form.get("endDate")

    # If no date range chosen, use trailing week
    if start_input and end_input:
        start = datetime.strptime(start_input, "%Y-%m-%d").date()
        end = datetime.strptime(end_input, "%Y-%m-%d").date()
    else:
        start = datetime.now().date() - timedelta(days=7)
        end = datetime.now().date()
    
    num_days = (end - start).days + 1

    date_range = [(start + timedelta(days=i)) for i in range(num_days)]
    str_date_range = [day.strftime("%m/%d/%Y") for day in date_range]

    event_infos = get_event_infos(start, end)
    labels_types = list({(info[0].label, info[3]) for info in event_infos})

    graph_colors = ['#4dc9f6', '#f67019', '#f53794', '#537bc4', '#acc236', 
                  '#166a8f', '#00a950', '#58595b', '#8549ba']

    datasets = []

    for i, label_type in enumerate(labels_types):
        # get min & max units for that label
        min_max = get_evt_type_min_max(label_type[1], label_type[0])
        label_min = min_max['min']
        label_max = min_max['max']
        
        # take max units for event label on given day, find % of label's range
        # later: ideally, make min max function find min and max based on day,
        #    not based on event occurrence
        day_percents = []
        for day in date_range:
            day_units = [info[2] for info in event_infos
                         if info[1].timestamp.date() == day
                         and info[0].label == label_type[0]]
            if label_max == label_min and day_units:
                unit_percent = 1
            elif label_max != label_min and day_units:
                unit_percent = (max(day_units) - label_min) / (label_max - label_min)
            else:
                unit_percent = 0
            day_percents.append(unit_percent)

        datasets.append({
            "label": label_type[0],
            "data": day_percents,
            "borderColor": graph_colors[i % len(graph_colors)],
            "borderWidth": 3,
            "fill": False
        })

    return json.dumps({"labels": str_date_range, "datasets": datasets})


def get_associated_events(evt_dates):
    """Get all even types associated with the given event type.

    Given a list of dates associated with an event type for the logged in User, 
    get all event types that had events occur on the same, prior, or following 
    day as given event type."""

    user = get_user()

    prior_dates = set()
    following_dates = set()

    # Add prior and following dates to dict of event dates
    for evt_date in evt_dates:
        prior_dates.add(evt_date - timedelta(days=1))
        following_dates.add(evt_date + timedelta(days=1))

    assoc_dates = evt_dates | prior_dates | following_dates

    # Get all events for user associated with those dates
    habit_evts = db.session.query(HabitEvent)\
                     .filter(HabitEvent.user == user).all()
    infl_evts = db.session.query(InfluenceEvent)\
                    .filter(InfluenceEvent.user == user).all()
    symp_evts = db.session.query(SymptomEvent)\
                    .filter(SymptomEvent.user == user).all()

    # Get all event labels associated with those dates
    assoc_habits = [habit_evt.habit.label for habit_evt in habit_evts
                    if habit_evt.timestamp.date() in assoc_dates]
    assoc_infls = [infl_evt.influence.label for infl_evt in infl_evts
                    if infl_evt.timestamp.date() in assoc_dates]
    assoc_symps = [symp_evt.symptom.label for symp_evt in symp_evts
                    if symp_evt.timestamp.date() in assoc_dates]

    # Return list of unique labels associated with given event type
    return list(set(assoc_habits + assoc_infls + assoc_symps))


@app.route("/bubble-chart-data")
def get_bubble_chart_data():
    """Get User's tracked data in JSON format for bubble chart."""

    user = get_user()
    event_types = []

    # For each event type's events, get the total units and associated dates
    for habit in user.habits:
        units = 0
        evt_dates = set()
        for habit_event in habit.habit_events:
            units += habit_event.num_units
            evt_dates.add(habit_event.timestamp.date())

        associations = get_associated_events(evt_dates)

        event_types.append({"type": "habit", "id": habit.id, "label": habit.label,
                        "units": units, "fill": "#f53794", "group": 0,
                        "associations": associations})

    for influence in user.influences:
        if influence.label != "weather" and influence.label != "temperature":
            units = 0
            evt_dates = set()
            for influence_event in influence.influence_events:
                units += influence_event.intensity
                evt_dates.add(influence_event.timestamp.date())

            associations = get_associated_events(evt_dates)

            event_types.append({"type": "influence", "id": influence.id,
                            "label": influence.label, "units": units,
                            "fill": "#f67019", "group": 1,
                            "associations": associations})

    for symptom in user.symptoms:
        units = 0
        evt_dates = set()
        for symptom_event in symptom.symptom_events:
            units += symptom_event.intensity
            evt_dates.add(symptom_event.timestamp.date())

        associations = get_associated_events(evt_dates)

        event_types.append({"type": "symptom", "id": symptom.id,
                        "label": symptom.label, "units": units,
                        "fill": "#4dc9f6", "group": 2,
                        "associations": associations})

    return json.dumps(event_types)


if __name__ == "__main__":
    app.debug = True
    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
