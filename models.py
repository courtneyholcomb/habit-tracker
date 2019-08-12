"""Models for habit tracker database tables."""


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Habit:
    """An type of activity that will be tracked by a User."""

    __tablename__ = "habits"

    habit_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    label = db.Column(db.String(30), nullable=False)
    unit = db.Column(db.String(20), nullable=False)


class User:
    """A person using the habit tracker."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(64), nullable=False)


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


class Goal:
    """A user-set goal: to do a Habit x times during x time period."""

    __tablename__ = "goals"

    goal_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.habit_id'))
    num_units = db.Column(db.Float, nullable=False)
    time_period = db.Columb(db.Interval, nullable=False)







