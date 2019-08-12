"""Models for habit tracker database tables."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """A person using the habit tracker."""

    __tablename__ = "users"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(64), nullable=False)

    habits = db.relationship("Habit", secondary="activities", backref="user")

    def __repr__(self):
        """Show User id and username."""

        return f"<User {self.id} {self.username}>"


class Habit(db.Model):
    """An type of activity that will be tracked by a User."""

    __tablename__ = "habits"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    label = db.Column(db.String(30), nullable=False)
    unit = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        """Show Habit id and label."""

        return f"<Habit {self.id} {self.label}>"


class Activity(db.Model):
    """An instance of a Habit completed by a User."""

    __tablename__ = "activities"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'))
    num_units = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float)    # ok for location columns to be null?
    longitude = db.Column(db.Float)

    user = db.relationship("User", uselist=False, backref="activities")
    habit = db.relationship("Habit", uselist=False, backref="activities")

    def __repr__(self):
        """Show Activity id, label, and associated User's username."""

        return f"<Activity {self.id} {self.habit.label} {self.user.username}>"


class Influence(db.Model):
    """Something that may passively influence a User, like the weather.""" 

    __tablename__ = "influences"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    label = db.Column(db.String(30), nullable=False)
    intensity = db.Column(db.Integer)   # ok for this to be null?
    timestamp = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    user = db.relationship("User", uselist=False, backref="influences")

    def __repr__(self):
        """Show Influence id, label, and associated User's username."""

        return f"<Influence {self.id} {self.label} {self.user.username}>"


class Symptom(db.Model):
    """A measurement of one aspect of a User's wellness."""

    __tablename__ = "symptoms"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    label = db.Column(db.String(50), nullable=False)
    intensity = db.Column(db.Integer) # ok for this to be null?
    timestamp = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    user = db.relationship("User", uselist=False, backref="symptoms")

    def __repr__(self):
        """Show Symptom id, label, and associated User's username."""

        return f"<Symptom {self.id} {self.label} {self.user.username}>"


class Goal(db.Model):
    """A user-set goal: to do a Habit x times during x time period."""

    __tablename__ = "goals"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'))
    num_units = db.Column(db.Float, nullable=False)
    time_period = db.Column(db.Interval, nullable=False)

    user = db.relationship("User", uselist=False, backref="goals")
    habit = db.relationship("Habit", uselist=False, backref="goals")

    def __repr__(self):
        """Show Goal id, associated Habit label, and associated username."""

        return f"<Goal {self.id} {self.habit.label} {self.user.username}>"


if __name__ == "__main__":
    # Connect to habit-tracker database when testing models interactively.
    # from server import app
    # connect_to_db(app)
    pass

