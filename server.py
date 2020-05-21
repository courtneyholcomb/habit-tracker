import requests
import json
import os
from datetime import datetime, timedelta, date, timezone
import time
import dateutil.parser
from tzlocal import get_localzone
import pytz
import pickle
import pdb

from flask import Flask, render_template, redirect, flash, request, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from models import (
    db,
    User,
    Habit,
    HabitEvent,
    Influence,
    InfluenceEvent,
    Symptom,
    SymptomEvent,
)
from scrape import get_ritual_classes


app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")


def connect_to_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///cultivate"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


### Routes to handle user registration, login, logout
@app.route("/")
def show_homepage():
    if "username" not in session:
        return redirect(url_for("show_login_form"))
    else:
        return redirect(url_for("show_track_page"))


@app.route("/login")
def show_login_form():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def validate_login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter(User.username == username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        session["username"] = username
        session["user_id"] = user.id
        flash("Login successful")
        return "OK", 200

    else:
        return "Incorrect username or password."


@app.route("/register")
def show_register_form():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confpass = request.form.get("confpass")

    ### Check that email & username are available
    if User.query.filter_by(email=email).first():
        return "There is already an account associated with that email."

    if User.query.filter_by(username=username).first():
        return "Username already taken."

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

        # Log the user in
        session["username"] = username
        session["user_id"] = new_user.id
        flash("Login successful")

        return "OK", 200


@app.route("/logout")
def log_out():
    session.clear()

    return redirect(url_for("show_login_form"))


def get_user():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        return user


### Routes to add new things to track
@app.route("/new")
def show_add_new_form():
    if get_user():
        return render_template("new.html")

    else:
        redirect(url_for("show_login_form"))


@app.route("/user-event-types")
def get_user_event_types():
    user = get_user()

    return json.dumps(
        {
            "habits": [habit.to_json() for habit in user.habits],
            "influences": [influence.to_json() for influence in user.influences],
            "symptoms": [symptom.to_json() for symptom in user.symptoms],
        }
    )


def validate_new_event_type(label):
    user = get_user()

    if Habit.query.filter(Habit.label == label, Habit.user == user).first():
        return "You already have a habit with that title."

    if Influence.query.filter(Influence.label == label, Influence.user == user).first():
        return "You already have an influence with that title."

    if Symptom.query.filter(Symptom.label == label, Symptom.user == user).first():
        return "You already have a symptom with that title."


@app.route("/new", methods=["POST"])
def add_new_event_type():
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

    if event_type == "habit":
        new_obj = Habit.query.filter(Habit.label == label, Habit.user == user).one()
        new_id = new_obj.id

    elif event_type == "influence":
        new_obj = Influence.query.filter(
            Influence.label == label, Influence.user == user
        ).one()
        new_id = new_obj.id

    elif event_type == "symptom":
        new_obj = Symptom.query.filter(
            Symptom.label == label, Symptom.user == user
        ).one()
        new_id = new_obj.id

    return json.dumps(
        {"new_id": new_id, "success": f"New {event_type} added successfully!"}
    )


### Routes to track events
@app.route("/track")
def show_track_page():
    user = get_user()

    if user:
        return render_template(
            "track.html",
            habits=user.habits,
            influences=user.influences,
            symptoms=user.symptoms,
        )
    else:
        return redirect(url_for("show_login_form"))


def create_event(
    evt_type, user_id, type_id, num, timestamp=datetime.now(), lat=None, lon=None
):
    user_id = session["user_id"]

    if evt_type == "habit":
        new_event = HabitEvent(
            user_id=user_id,
            habit_id=type_id,
            num_units=num,
            timestamp=timestamp,
            latitude=lat,
            longitude=lon,
        )
    elif evt_type == "influence":
        new_event = InfluenceEvent(
            user_id=user_id,
            influence_id=type_id,
            intensity=num,
            timestamp=timestamp,
            latitude=lat,
            longitude=lon,
        )
    elif evt_type == "symptom":
        new_event = SymptomEvent(
            user_id=user_id,
            symptom_id=type_id,
            intensity=num,
            timestamp=timestamp,
            latitude=lat,
            longitude=lon,
        )
    db.session.add(new_event)
    db.session.commit()


@app.route("/track", methods=["POST"])
def track_something():
    user_id = session["user_id"]
    num = request.form.get("num")
    evt_type = request.form.get("eventType")
    type_id = request.form.get("typeId")
    location = request.form.get("location")
    lat = None
    lon = None
    # pdb.set_trace()

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
    user_id = session["user_id"]
    timestamp = datetime.now()

    # Get current weather from Open Weather API for given lat & lon
    weather_token = os.environ.get("WEATHER_TOKEN")
    response_obj = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&APPID={weather_token}"
    )
    weather_info = response_obj.json()
    weather_id = weather_info["weather"][0]["id"]

    temp_info = weather_info["main"]
    current_temp_f = 9 / 5 * (temp_info["temp"] - 273) + 32

    temp_infl = ensure_tracking_infl("temperature", 125)
    weather_infl = ensure_tracking_infl("weather", 1000)

    # Add temp & weather events to db
    create_event(
        "influence", user_id, temp_infl.id, current_temp_f, timestamp, lat, lon
    )
    create_event("influence", user_id, weather_infl.id, weather_id, timestamp, lat, lon)


def ensure_tracking_infl(label, scale):
    infl = Influence.query.filter_by(label=label).first()

    if infl:
        return infl

    else:
        new_infl = Influence(label=label, scale=scale, user_id=user_id)
        db.session.add(new_infl)
        db.session.commit()
        return new_infl


def enable_gcal():
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

    user = get_user()
    creds = user.gcal_token

    # If no valid creds, prompt login.
    if not creds or not creds.valid:
        # if creds are expired but renewable, renew them.
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # prompt login
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials to db
        user.gcal_token = creds
        db.session.commit()

    return build("calendar", "v3", credentials=creds)


@app.route("/track-gcal-habits", methods=["POST"])
def get_gcal_events():
    user = get_user()
    dt_start = request.form.get("startDate")
    dt_end = request.form.get("endDate")
    habits = user.habits
    gcal_info = enable_gcal()

    if not dt_start:
        dt_start = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
    else:
        dt_start = dateutil.parser.parse(dt_start).isoformat() + "Z"
    if not dt_end:
        dt_end = datetime.utcnow().isoformat() + "Z"
    else:
        dt_end = dateutil.parser.parse(dt_end).isoformat() + "Z"

    calendars = gcal_info.calendarList().list().execute()["items"]
    events = []

    for calendar in calendars:
        events_result = (
            gcal_info.events()
            .list(
                calendarId=calendar["id"],
                timeMin=dt_start,
                timeMax=dt_end,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events += events_result["items"]

    # If any GCal events in time range have habit labels in title, track them.
    events_tracked = ""
    for event in events:
        # Get info from event
        start = event["start"].get("dateTime", event["start"].get("date"))
        start_format = start[:10]
        if len(start) > 11:
            reformat_time = datetime.strptime(start[11:16], "%H:%M").strftime(
                "%I:%M %p"
            )
            start_format += " " + reformat_time
        end = event["end"].get("dateTime", event["end"].get("date"))
        title = event["summary"]
        title_words = set(title.lower().split())

        for habit in habits:
            if habit.label.lower() in title_words:

                # Check if event is already tracked
                duplicate = HabitEvent.query.filter(
                    HabitEvent.user_id == user.id,
                    HabitEvent.timestamp == start,
                    HabitEvent.habit_id == habit.id,
                ).first()

                if not duplicate:
                    create_event("habit", user.id, habit.id, 1, start)
                    events_tracked += (
                        f"\nHabit – {habit.label}\n"
                        f"Event – {title} ({start_format})\n"
                    )

    return events_tracked


### View your data + charts
@app.route("/charts")
def show_charts_page():
    return render_template("charts.html")


def get_events_in_range(start, end):
    user = get_user()

    habit_events = HabitEvent.query.filter(
        HabitEvent.timestamp.between(start, end), HabitEvent.user == user
    ).all()

    influence_events = InfluenceEvent.query.filter(
        InfluenceEvent.timestamp.between(start, end), InfluenceEvent.user == user
    ).all()

    symptom_events = SymptomEvent.query.filter(
        SymptomEvent.timestamp.between(start, end), SymptomEvent.user == user
    ).all()

    return {
        "habit_events": habit_events,
        "influence_events": influence_events,
        "symptom_events": symptom_events,
    }


def get_evt_type_min_max(evt_type, label):
    user = get_user()

    if evt_type == "habit":
        type_option = Habit.query.filter(Habit.user == user, Habit.label == label).one()
        units = [evt.num_units for evt in type_option.habit_events]

    elif evt_type == "influence":
        type_option = Influence.query.filter(
            Influence.user == user, Influence.label == label
        ).one()
        units = [evt.intensity for evt in type_option.influence_events]

    elif evt_type == "symptom":
        type_option = Symptom.query.filter(
            Symptom.user == user, Symptom.label == label
        ).one()
        units = [evt.intensity for evt in type_option.symptom_events]

    return {"min": min(units), "max": max(units)}


def get_event_infos(start, end):
    events_dict = get_events_in_range(start, end)
    habit_events = events_dict["habit_events"]
    influence_events = events_dict["influence_events"]
    symptom_events = events_dict["symptom_events"]

    habit_event_info = [
        (habit_event.habit, habit_event, habit_event.num_units, "habit")
        for habit_event in habit_events
    ]

    influence_event_info = [
        (
            influence_event.influence,
            influence_event,
            influence_event.intensity,
            "influence",
        )
        for influence_event in influence_events
        if influence_event.influence.label != "weather"
    ]

    symptom_event_info = [
        (symptom_event.symptom, symptom_event, symptom_event.intensity, "symptom")
        for symptom_event in symptom_events
    ]

    event_infos = habit_event_info + influence_event_info + symptom_event_info

    return event_infos


@app.route("/line-chart-data", methods=["POST"])
def get_line_chart_data():
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

    graph_colors = [
        "#689689",  # light blue
        "#DC9E82",  # orange
        "#D87B7D",  # pink
        "#537bc4",  # periwinkle
        "#acc236",  # light green
        "#166a8f",  # grey blue
        "#00a950",  # kelly green
        "#58595b",  # grey
        "#8549ba",  # purple
    ]

    datasets = []

    for i, label_type in enumerate(labels_types):
        # get min & max units for that label
        min_max = get_evt_type_min_max(label_type[1], label_type[0])
        label_min = min_max["min"]
        label_max = min_max["max"]

        # take max units for event label on given day, find % of label's range
        # later: ideally, make min max function find min and max based on day,
        #    not based on event occurrence
        day_percents = []
        for day in date_range:
            day_units = [
                info[2]
                for info in event_infos
                if info[1].timestamp.date() == day and info[0].label == label_type[0]
            ]
            if label_max == label_min and day_units:
                unit_percent = 1
            elif label_max != label_min and day_units:
                unit_percent = (max(day_units) - label_min) / (label_max - label_min)
            else:
                unit_percent = 0
            day_percents.append(unit_percent)

        datasets.append(
            {
                "label": label_type[0],
                "data": day_percents,
                "borderColor": graph_colors[i % len(graph_colors)],
                "borderWidth": 3,
                "fill": False,
            }
        )

    return json.dumps({"labels": str_date_range, "datasets": datasets})


def get_associated_events(evt_dates):
    """Given a list of dates when a given event type occurred for the logged in User, 
    get all event types that occurred on the same, prior, or following day as given event type."""

    user = get_user()

    prior_dates = set()
    following_dates = set()

    # Add prior and following dates to dict of event dates
    for evt_date in evt_dates:
        prior_dates.add(evt_date - timedelta(days=1))
        following_dates.add(evt_date + timedelta(days=1))

    assoc_dates = evt_dates | prior_dates | following_dates

    # Get all events for user associated with those dates
    habit_evts = HabitEvent.query.filter(HabitEvent.user == user).all()
    infl_evts = InfluenceEvent.query.filter(InfluenceEvent.user == user).all()
    symp_evts = SymptomEvent.query.filter(SymptomEvent.user == user).all()

    # Get all event labels associated with those dates
    assoc_habits = [
        habit_evt.habit.label
        for habit_evt in habit_evts
        if habit_evt.timestamp.date() in assoc_dates
    ]
    assoc_infls = [
        infl_evt.influence.label
        for infl_evt in infl_evts
        if infl_evt.timestamp.date() in assoc_dates
    ]
    assoc_symps = [
        symp_evt.symptom.label
        for symp_evt in symp_evts
        if symp_evt.timestamp.date() in assoc_dates
    ]

    # Return list of unique labels associated with given event type
    return list(set(assoc_habits + assoc_infls + assoc_symps))


@app.route("/bubble-chart-data")
def get_bubble_chart_data():
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

        event_types.append(
            {
                "type": "habit",
                "id": habit.id,
                "label": habit.label,
                "units": units,
                "fill": "#D87B7D",
                "group": 0,
                "associations": associations,
            }
        )

    for influence in user.influences:
        if influence.label != "weather" and influence.label != "temperature":
            units = 0
            evt_dates = set()
            for influence_event in influence.influence_events:
                units += influence_event.intensity
                evt_dates.add(influence_event.timestamp.date())

            associations = get_associated_events(evt_dates)

            event_types.append(
                {
                    "type": "influence",
                    "id": influence.id,
                    "label": influence.label,
                    "units": units,
                    "fill": "#DC9E82",
                    "group": 1,
                    "associations": associations,
                }
            )

    for symptom in user.symptoms:
        units = 0
        evt_dates = set()
        for symptom_event in symptom.symptom_events:
            units += symptom_event.intensity
            evt_dates.add(symptom_event.timestamp.date())

        associations = get_associated_events(evt_dates)

        event_types.append(
            {
                "type": "symptom",
                "id": symptom.id,
                "label": symptom.label,
                "units": units,
                "fill": "#B2E6D4",
                "group": 2,
                "associations": associations,
            }
        )

    return json.dumps(event_types)


### YOGA CLASS PICKER!
@app.route("/class-picker")
def show_class_picker():
    return render_template("class-picker.html")


@app.route("/la-class-picker")
def show_la_class_picker():
    return render_template("la-class-picker.html")


@app.route("/yoga-classes")
def get_yoga_classes():
    date_input = request.args.get("dateInput")
    start_input = request.args.get("start")
    end_input = request.args.get("end")
    local_tz = get_localzone()
    pst = pytz.timezone("US/Pacific")
    local_tz = get_localzone()

    user_location = request.args.get("location")
    gmaps_token = os.environ.get("GMAPS_TOKEN")
    gm_url_1 = "https://maps.googleapis.com/maps/api/directions/json"

    # If no time entered, start = now and end = 6 hours from now
    if date_input and start_input and end_input:
        start = datetime.strptime(date_input + start_input, "%Y-%m-%d%H:%M").astimezone(
            pst
        )
        end = datetime.strptime(date_input + end_input, "%Y-%m-%d%H:%M").astimezone(pst)
    else:
        start = datetime.now().astimezone(pst)
        end = start + timedelta(hours=6)

    ### Get info for Mindbody classes
    # Prep info for mindbody get requests
    mindbody = (
        "https://prod-mkt-gateway.mindbody.io/v1/search/class_times?sort"
        "=start_time&page.size=100&page.number=1&filter.category_types=Fitness"
        f"&filter.inventory_source=MB&filter.start_time_from={start.astimezone(pytz.utc).isoformat() + 'Z'}"
        f"&filter.start_time_to={end.astimezone(pytz.utc).isoformat() + 'Z'}&filter.dynamic_priceable=any"
        "&filter.include_dynamic_pricing=true&filter.location_slug="
    )

    mb_locations = [
        "love-story-yoga-mission-dolores",
        "yoga-tree-6",
        "yoga-tree-5",
        "yoga-tree-3",
        "yoga-tree-2",
        "astayoga-mission-dolores",
        "mission-yoga-mission-district",
        "moxie-yoga-fitness-mission-district",
        "moxie-yoga-fitness-bernal-heights",
    ]

    # Get class data from all mindbody locations
    mb_classes = []
    for location in mb_locations:
        data = requests.get(mindbody + location).json()["data"]
        mb_classes.extend(data)

    data_list = []
    # Extract individual class info from mindbody JSON response
    for clas in mb_classes:
        info = clas["attributes"]
        clas_end = (
            dateutil.parser.parse(info["class_time_end_time"])
            .astimezone(pytz.utc)
            .astimezone(pst)
        )
        duration = info["class_time_duration"]
        clas_start = (
            dateutil.parser.parse(info["class_time_start_time"])
            .astimezone(pytz.utc)
            .astimezone(pst)
        )
        title = info["course_name"]

        # Eliminate classes outside of availability + classes w/ bad keywords
        bad_kws = ["kundalini", "yin", "light", "therapeutic", "recover", "buti"]
        if not any(kw in title.lower() for kw in bad_kws) and clas_end <= end:
            address = info["location_address"] + ", SF"
            # If user gave location, get travel time to studio
            if user_location:
                gm_url_2 = (
                    f"?origin={user_location}&destination={address}"
                    f"&key={gmaps_token}&mode="
                )

                transit_time = requests.get(gm_url_1 + gm_url_2 + "transit").json()[
                    "routes"
                ][0]["legs"][0]["duration"]["text"]
                biking_time = requests.get(gm_url_1 + gm_url_2 + "bicycling").json()[
                    "routes"
                ][0]["legs"][0]["duration"]["text"]
                travel_time = min(transit_time, biking_time)
            else:
                transit_time = ""
                biking_time = ""
                travel_time = "0 mins"

            # Eliminate classes user can't travel to in time
            if "hour" not in travel_time:
                travel_dt = timedelta(minutes=int(travel_time[:-5]))
                if (start + travel_dt) <= clas_start:

                    # For all classes that meet requirements, get remaining info
                    studio = info["location_name"]
                    brand = info["location_business_name"]
                    if "MOXIE" in studio:
                        studio = f"{studio[:5]} {info['location_neighborhood']}"
                    if "Yoga Tree" in brand:
                        studio = f"{brand} {studio}"

                    instructor = info["instructor_name"]

                    # Add info from each class in time range to data_list
                    data_list.append(
                        {
                            "studio": studio,
                            "title": title,
                            "instructor": instructor,
                            "duration": duration,
                            "start": clas_start.strftime("%-I:%M%p"),
                            "end": clas_end.strftime("%-I:%M%p"),
                            "address": address,
                            "travel": travel_time,
                            "transit": transit_time,
                            "biking": biking_time,
                        }
                    )

    ### Get info for CorePower classes
    # Prep info needed for corepower get requests
    cp_start = "https://d2244u25cro8mt.cloudfront.net/locations/1419/"
    cp_locations = ["73", "45", "65", "67"]
    cp_end = f"/classes/{start.date()}/{end.date()}"
    cp_addresses = {
        "Hayes Valley": "150 Van Ness Ave Suite A",
        "Fremont": "215 Fremont Street",
        "FIDI": "241 California Street",
        "Duboce": "100 Church Street, SF",
    }

    # Get class data from each corepower location
    cp_classes = []
    for location in cp_locations:
        cp_classes.extend(requests.get(cp_start + location + cp_end).json())

    # Extract individual class info from corepower JSON response
    for clas in cp_classes:
        clas_start = dateutil.parser.parse(clas["start_date_time"][:-1]).astimezone(pst)
        clas_end = dateutil.parser.parse(clas["end_date_time"][:-1]).astimezone(pst)
        title = clas["name"]

        # Eliminate those out of input time range + sculpt/c1 classes
        if (
            clas_start >= start
            and clas_end <= end
            and not "Sculpt" in title
            and not "C1" in title
        ):

            # If user gave location, get travel time to studio
            studio = clas["location"]["name"][6:]
            address = cp_addresses[studio]

            # If user gave location, get travel time to studio
            if user_location:
                gm_url_2 = f"?origin={user_location}&destination={address}&key={gmaps_token}&mode="
                transit_time = requests.get(gm_url_1 + gm_url_2 + "transit").json()[
                    "routes"
                ][0]["legs"][0]["duration"]["text"]
                biking_time = requests.get(gm_url_1 + gm_url_2 + "bicycling").json()[
                    "routes"
                ][0]["legs"][0]["duration"]["text"]
                travel_time = min(transit_time, biking_time)
            else:
                transit_time = ""
                biking_time = ""
                travel_time = "0 mins"

            # Eliminate classes user can't travel to in time
            travel_td = timedelta(minutes=int(travel_time[:-5]))
            if (start + travel_td) <= clas_start:

                # For all classes that meet requirements, get remaining info
                start_format = clas_start.strftime("%-I:%M%p")
                end_format = clas_end.strftime("%-I:%M%p")
                instructor = clas["teacher"]["name"]
                duration = (clas_end - clas_start).total_seconds() / 60

                # add info from each class in time range to data_list
                data_list.append(
                    {
                        "studio": "CorePower " + studio,
                        "title": title,
                        "instructor": instructor,
                        "start": start_format,
                        "end": end_format,
                        "duration": duration,
                        "address": address,
                        "travel": travel_time,
                        "transit": transit_time,
                        "biking": biking_time,
                    }
                )

    ### Get info for Ritual classes
    ritual_classes = get_ritual_classes(start, end)

    for ritual_class in ritual_classes:

        if user_location:
            gm_url_2 = (
                f"?origin={user_location}&destination={address}"
                f"&key={gmaps_token}&mode="
            )
            transit_time = requests.get(gm_url_1 + gm_url_2 + "transit").json()[
                "routes"
            ][0]["legs"][0]["duration"]["text"]
            biking_time = requests.get(gm_url_1 + gm_url_2 + "bicycling").json()[
                "routes"
            ][0]["legs"][0]["duration"]["text"]
            travel_time = min(transit_time, biking_time)
        else:
            transit_time = ""
            biking_time = ""
            travel_time = "0 mins"

        # Eliminate classes user can't travel to in time
        travel_td = timedelta(minutes=int(travel_time[:-5]))
        if start + travel_td <= ritual_class["start"]:

            # Add travel time to class info + add info to data list
            ritual_class["travel"] = travel_time
            ritual_class["transit"] = transit_time
            ritual_class["biking"] = biking_time
            ritual_class["start"] = ritual_class["start"].strftime("%-I:%M%p")
            ritual_class["end"] = ritual_class["end"].strftime("%-I:%M%p")
            data_list.append(ritual_class)

    return json.dumps(data_list)


@app.route("/la-yoga-classes")
def get_la_yoga_classes():
    date_input = request.args.get("dateInput")
    start_input = request.args.get("start")
    end_input = request.args.get("end")
    pst = pytz.timezone("US/Pacific")
    local_tz = get_localzone()

    # If no time entered, start = now and end = 6 hours from now
    if date_input and start_input and end_input:
        start = datetime.strptime(date_input + start_input, "%Y-%m-%d%H:%M").astimezone(
            pst
        )
        end = datetime.strptime(date_input + end_input, "%Y-%m-%d%H:%M").astimezone(pst)
    else:
        start = datetime.now().astimezone(pst)
        end = start + timedelta(hours=6)

    ### Get info for Mindbody classes
    # Prep info for mindbody get requests
    mindbody = (
        "https://prod-mkt-gateway.mindbody.io/v1/search/class_times?sort"
        "=start_time&page.size=100&page.number=1&filter.category_types=Fitness"
        f"&filter.inventory_source=MB&filter.start_time_from={start.astimezone(pytz.utc).isoformat() + 'Z'}"
        f"&filter.start_time_to={end.astimezone(pytz.utc).isoformat() + 'Z'}&filter.dynamic_priceable=any"
        "&filter.include_dynamic_pricing=true&filter.location_slug="
    )

    mb_locations = ["yoga-jaya", "yoga-blend", "yoga-noho-noho", "the-wellness-of-oz"]

    # Get class data from all mindbody locations
    mb_classes = []
    for location in mb_locations:
        data = requests.get(mindbody + location).json()["data"]
        mb_classes.extend(data)

    data_list = []
    # Extract individual class info from mindbody JSON response
    for clas in mb_classes:
        info = clas["attributes"]
        clas_end = (
            dateutil.parser.parse(info["class_time_end_time"])
            .astimezone(pytz.utc)
            .astimezone(pst)
        )
        duration = info["class_time_duration"]
        clas_start = (
            dateutil.parser.parse(info["class_time_start_time"])
            .astimezone(pytz.utc)
            .astimezone(pst)
        )
        title = info["course_name"]

        # Eliminate classes outside of availability + classes w/ bad keywords
        # bad_kws = ["kundalini", "yin", "light", "therapeutic", "recover", "buti"]
        # if not any(kw in title.lower() for kw in bad_kws) and
        if clas_end <= end and start <= clas_start:
            studio = info["location_name"]
            instructor = info["instructor_name"]

            # Add info from each class in time range to data_list
            data_list.append(
                {
                    "studio": studio,
                    "title": title,
                    "instructor": instructor,
                    "duration": duration,
                    "start": clas_start.strftime("%-I:%M%p"),
                    "end": clas_end.strftime("%-I:%M%p"),
                }
            )

    ### Get info for CorePower classes
    # Prep info needed for corepower get requests
    cp_start = "https://d2244u25cro8mt.cloudfront.net/locations/1419/"
    cp_locations = ["32", "30", "12"]
    cp_end = f"/classes/{start.date()}/{end.date()}"

    # Get class data from each corepower location
    cp_classes = []
    for location in cp_locations:
        cp_classes.extend(requests.get(cp_start + location + cp_end).json())

    # Extract individual class info from corepower JSON response
    for clas in cp_classes:
        clas_start = dateutil.parser.parse(clas["start_date_time"][:-1]).astimezone(pst)
        clas_end = dateutil.parser.parse(clas["end_date_time"][:-1]).astimezone(pst)
        title = clas["name"]

        # Eliminate those out of input time range + sculpt/c1 classes
        if clas_start >= start and clas_end <= end and not "Sculpt" in title:
            studio = clas["location"]["name"][3:]

            # For all classes that meet requirements, get remaining info
            start_format = clas_start.strftime("%-I:%M%p")
            end_format = clas_end.strftime("%-I:%M%p")
            instructor = clas["teacher"]["name"]
            duration = (clas_end - clas_start).total_seconds() / 60

            # add info from each class in time range to data_list
            data_list.append(
                {
                    "studio": "CorePower " + studio,
                    "title": title,
                    "instructor": instructor,
                    "start": start_format,
                    "end": end_format,
                    "duration": duration,
                }
            )

    return json.dumps(data_list)


if __name__ == "__main__":
    app.debug = False
    connect_to_db(app)
    # DebugToolbarExtension(app)

    app.run(port=5000, host="0.0.0.0")
