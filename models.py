"""Models for habit tracker database tables."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User:
    """A person using the habit tracker."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(64), nullable=False)

    habits = db.relationship("Habit", secondary="activites", backref="user")

    # def __repr__(self):
    #     """Show user details."""

    #     return "<User user_id={{user_id}}, email={{email}}, "\
    #            "username={{username}}>"


class Habit:
    """An type of activity that will be tracked by a User."""

    __tablename__ = "habits"

    habit_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    label = db.Column(db.String(30), nullable=False)
    unit = db.Column(db.String(20), nullable=False)


class Activity:
    """An instance of a Habit completed by a User."""

    __tablename__ = "activities"

    activity_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.habit_id'))
    num_units = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float)    # ok for location columns to be null?
    longitude = db.Column(db.Float)

    user = db.relationship("User", uselist=False, backref="activities")
    habit = db.relationship("Habit", uselist=False, backref="activities")


class Influence:
    """Something that may passively influence a User, like the weather.""" 

    __tablename__ = "influences"

    influence_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    label = db.Column(db.String(30), nullable=False)
    intensity = db.Column(db.Integer)   # ok for this to be null?
    timestamp = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    user = db.relationship("User", uselist=False, backref="influences")


class Symptom:
    """A measurement of one aspect of a User's wellness."""

    __tablename__ = "symptoms"

    symptom_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    label = db.Column(db.String(50), nullable=False)
    intensity = db.Column(db.Integer) # ok for this to be null?
    timestamp = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    user = db.relationship("User", uselist=False, backref="symptoms")


class Goal:
    """A user-set goal: to do a Habit x times during x time period."""

    __tablename__ = "goals"

    goal_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.habit_id'))
    num_units = db.Column(db.Float, nullable=False)
    time_period = db.Column(db.Interval, nullable=False)

    user = db.relationship("User", uselist=False, backref="goals")
    habit = db.relationship("Habit", uselist=False, backref="goals")


def connect_to_db(app):
    """Connect Flask app to habit-tracker database."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///habit-tracker'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # Connect to habit-tracker database when testing models interactively.
    from server import app
    connect_to_db(app)


