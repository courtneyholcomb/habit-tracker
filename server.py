"""Routes for habit tracker."""

from flask import Flask
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


# @app.route("/")






# register new user
# add new habit/influence/symptom to track
# track habit event/influence event/symptom event
# view data










if __name__ == "__main__":
    connect_to_db(app)