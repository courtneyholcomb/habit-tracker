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


### Routes to add new things to track
@app.route("/new")
def show_add_new_form():
    """Show the page where you can create a new Habit, Influence, or Symptom."""

    if "user_id" in session:
        user = User.query.get(session["user_id"])
        return render_template("new.html")

    else:
        redirect(url_for('show_login_form'))


@app.route("/user-event-types")
def get_user_event_types():
    """Get JSON of all Habits, Influences, and Symptoms for logged in User."""

    user = User.query.get(session["user_id"])

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

    user = User.query.get(session["user_id"])

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

    user = User.query.get(session["user_id"])

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
        


### routes to track events
@app.route("/track")
def show_track_page():
    """Show the page where you can track a Habit, Influence, or Symptom."""

    if "user_id" in session:
        user = User.query.get(session["user_id"])
        return render_template("track.html")
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
    weather_id = weather_info['weather'][0]['id']

    temp_info = weather_info['main']
    current_temp_f = 9 / 5 * (temp_info['temp'] - 273) + 32

    user_id = session["user_id"]
    timestamp = datetime.now()
    
    # if user doesn't track temp & weather yet, add them
    try:
        temp_infl = Influence.query.filter_by(label="temperature").one()
    except:
        new_infl = Influence(label="temperature", scale=125, user_id=user_id)
        db.session.add(new_infl)
        db.session.commit()
        temp_infl = Influence.query.filter_by(label="temperature").one()

    try:
        weather_infl = Influence.query.filter_by(label='weather').one()
    except:
        new_infl = Influence(label="weather", scale=1000, user_id=user_id)
        db.session.add(new_infl)
        db.session.commit()
        weather_infl = Influence.query.filter_by(label='weather').one()

    # instantiate temp & weather events
    temp_event = InfluenceEvent(user_id=user_id, influence_id=temp_infl.id,
                                intensity=current_temp_f, timestamp=timestamp,
                                latitude=lat, longitude=lon)

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

    dt_start = request.form.get("startDate")
    dt_end = request.form.get("endDate")

    if not dt_start:
        dt_start = (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z'
    if not dt_end:
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

### view your data
@app.route("/charts")
def show_charts_page():
    """Show page with User's charts."""

    return render_template("charts.html")


@app.route("/line1-data", methods=["POST"])
def get_line1_data():
    """Get data needed for chart with id = line1."""

    user = User.query.get(session["user_id"])
    start_input = request.form.get("startDate")
    end_input = request.form.get("endDate")

    if start_input and end_input:
        start = datetime.strptime(start_input, "%Y-%m-%d").date()
        end = datetime.strptime(end_input, "%Y-%m-%d").date()
    else:
        start = datetime.now().date() - timedelta(days=7)
        end = datetime.now().date()
    
    num_days = (end - start).days + 1

    date_range = [(start + timedelta(days=i)) for i in range(num_days)]
    str_date_range = [day.strftime("%m/%d/%Y") for day in date_range]

    # get info for all events that took place during selected time period
    habit_events = db.session.query(HabitEvent).filter(HabitEvent.timestamp
        .between(start, end), HabitEvent.user == user).all()

    habit_event_info = [(habit_event.habit, habit_event, habit_event.num_units)
                         for habit_event in habit_events]

    influence_events = db.session.query(InfluenceEvent).filter(
        InfluenceEvent.timestamp.between(start, end),
        InfluenceEvent.user == user).all()

    influence_event_info = [(influence_event.influence, influence_event,
                             influence_event.intensity)
                            for influence_event in influence_events
                            if influence_event.influence.label != "weather"]

    symptom_events = db.session.query(SymptomEvent).filter(
        SymptomEvent.timestamp.between(start, end),
        SymptomEvent.user == user).all()

    symptom_event_info = [(symptom_event.symptom, symptom_event,
                           symptom_event.intensity)
                          for symptom_event in symptom_events]

    events = habit_events + influence_events + symptom_events
    event_infos = habit_event_info + influence_event_info + symptom_event_info
    event_labels = list(set(info[0].label for info in event_infos))

    graph_colors = ['#4dc9f6', '#f67019', '#f53794', '#537bc4', '#acc236', 
                  '#166a8f', '#00a950', '#58595b', '#8549ba']

    datasets = []

    for i, event_label in enumerate(event_labels):
        # day_units = sum of units for given event type on given day
        day_units = []
        for day in date_range:
            unit_list = [info[2] for info in event_infos
                         if info[1].timestamp.date() == day
                         and info[0].label == event_label]
            day_units.append(sum(unit_list))

        datasets.append({
            "label": event_label,
            "data": day_units,
            "borderColor": graph_colors[i % len(graph_colors)],
            "borderWidth": 3,
            "fill": False
        })

    return json.dumps({"labels": str_date_range, "datasets": datasets})



@app.route("/bubble-chart-data")
def get_bubble_chart_data():
    """Get User's tracked data in JSON format for bubble chart."""

    user = User.query.get(session["user_id"])

    all_habit_evts = db.session.query(HabitEvent).filter(HabitEvent.user == user).all()
    all_infl_evts = db.session.query(InfluenceEvent).filter(InfluenceEvent.user == user).all()
    all_symp_evts = db.session.query(SymptomEvent).filter(SymptomEvent.user == user).all()

    event_types = []

    for habit in user.habits:
        total_units = 0
        evt_dates = {}
        for habit_event in habit.habit_events:
            total_units += habit_event.num_units
            evt_date = habit_event.timestamp.date()
            evt_dates[evt_date] = evt_dates.get(evt_date, 0) + habit_event.num_units

        assoc_habits = [habit_evt.habit.label for habit_evt in all_habit_evts
                        if habit_evt.timestamp.date() in evt_dates
                        or (habit_evt.timestamp.date() - timedelta(days=1)) in evt_dates
                        or (habit_evt.timestamp.date() + timedelta(days=1)) in evt_dates]
        assoc_infls = [infl_evt.influence.label for infl_evt in all_infl_evts
                        if infl_evt.timestamp.date() in evt_dates
                        or (infl_evt.timestamp.date() - timedelta(days=1)) in evt_dates
                        or (infl_evt.timestamp.date() + timedelta(days=1)) in evt_dates]
        assoc_symps = [symp_evt.symptom.label for symp_evt in all_symp_evts
                        if symp_evt.timestamp.date() in evt_dates
                        or (symp_evt.timestamp.date() - timedelta(days=1)) in evt_dates
                        or (symp_evt.timestamp.date() + timedelta(days=1)) in evt_dates]
        associations = list(set(assoc_habits + assoc_infls + assoc_symps))

        event_types.append({"type": "habit", "id": habit.id, "label": habit.label,
                        "units": total_units, "fill": "#f53794", "group": 0,
                        "associations": associations})

    for influence in user.influences:
        if influence.label != "weather" and influence.label != "temperature":
            total_units = 0
            evt_dates = {}
            for influence_event in influence.influence_events:
                total_units += influence_event.intensity
                evt_date = influence_event.timestamp.date()
                evt_dates[evt_date] = evt_dates.get(evt_date, 0) + influence_event.intensity

            assoc_habits = [habit_evt.habit.label for habit_evt in all_habit_evts
                            if habit_evt.timestamp.date() in evt_dates
                        or (habit_evt.timestamp.date() - timedelta(days=1)) in evt_dates
                        or (habit_evt.timestamp.date() + timedelta(days=1)) in evt_dates]
            assoc_infls = [infl_evt.influence.label for infl_evt in all_infl_evts
                            if infl_evt.timestamp.date() in evt_dates
                        or (infl_evt.timestamp.date() - timedelta(days=1)) in evt_dates
                        or (infl_evt.timestamp.date() + timedelta(days=1)) in evt_dates]
            assoc_symps = [symp_evt.symptom.label for symp_evt in all_symp_evts
                            if symp_evt.timestamp.date() in evt_dates
                        or (symp_evt.timestamp.date() - timedelta(days=1)) in evt_dates
                        or (symp_evt.timestamp.date() + timedelta(days=1)) in evt_dates]
            associations = list(set(assoc_habits + assoc_infls + assoc_symps))

            event_types.append({"type": "influence", "id": influence.id,
                            "label": influence.label, "units": total_units,
                            "fill": "#f67019", "group": 1,
                            "associations": associations})

    for symptom in user.symptoms:
        total_units = 0
        evt_dates = {}
        for symptom_event in symptom.symptom_events:
            total_units += symptom_event.intensity
            evt_date = symptom_event.timestamp.date()
            evt_dates[evt_date] = evt_dates.get(evt_date, 0) + symptom_event.intensity

        assoc_habits = [habit_evt.habit.label for habit_evt in all_habit_evts
                        if habit_evt.timestamp.date() in evt_dates
                        or (habit_evt.timestamp.date() - timedelta(days=1)) in evt_dates
                        or (habit_evt.timestamp.date() + timedelta(days=1)) in evt_dates]
        assoc_infls = [infl_evt.influence.label for infl_evt in all_infl_evts
                        if infl_evt.timestamp.date() in evt_dates
                        or (infl_evt.timestamp.date() - timedelta(days=1)) in evt_dates
                        or (infl_evt.timestamp.date() + timedelta(days=1)) in evt_dates]
        assoc_symps = [symp_evt.symptom.label for symp_evt in all_symp_evts
                        if symp_evt.timestamp.date() in evt_dates
                        or (symp_evt.timestamp.date() - timedelta(days=1)) in evt_dates
                        or (symp_evt.timestamp.date() + timedelta(days=1)) in evt_dates]
        associations = list(set(assoc_habits + assoc_infls + assoc_symps))

        event_types.append({"type": "symptom", "id": symptom.id,
                        "label": symptom.label, "units": total_units,
                        "fill": "#4dc9f6", "group": 2,
                        "associations": associations})

    return json.dumps(event_types)







if __name__ == "__main__":
    app.debug = True
    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
