"""Models for habit tracker."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



class User(db.Model):
    """A person using the habit tracker."""

    __tablename__ = "users"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    gcal_token = db.Column(db.PickleType)

    habits = db.relationship("Habit", backref="user")
    influences = db.relationship("Influence", backref="user")
    symptoms = db.relationship("Symptom", backref="user")

    def __str__(self):
        """Show User id and username."""

        return f"<User {self.id} {self.username}>"


class Habit(db.Model):
    """An activity that will be tracked by a User."""

    __tablename__ = "habits"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    label = db.Column(db.String(30), nullable=False)
    unit = db.Column(db.String(20))

    def __str__(self):
        """Show Habit id and label."""

        return f"<Habit {self.id} {self.label} {self.user.username}>"


class HabitEvent(db.Model): # rename: habit occurrence
    """An instance of a Habit completed by a User."""

    __tablename__ = "habit_events"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    habit_id = db.Column(db.Integer, db.ForeignKey("habits.id"))
    num_units = db.Column(db.Float) # if units null in habit, can be null here
    timestamp = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float)    # ok for location columns to be null?
    longitude = db.Column(db.Float)

    user = db.relationship("User", uselist=False, backref="habit_events")
    habit = db.relationship("Habit", uselist=False, backref="habit_events")

    def __str__(self):
        """Show HabitEvent id, label, and associated User's username."""

        return f"<HabitEvent {self.id} {self.habit.label} {self.user.username}>"


class Influence(db.Model):
    """Something that may passively experienced by a User, like the weather.""" 

    __tablename__ = "influences"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    label = db.Column(db.String(30), nullable=False)
    scale = db.Column(db.String(20))     # nullable

    def __str__(self):
        """Show Influence id, label, and associated User's username."""

        return f"<Influence {self.id} {self.label} {self.user.username}>"


class InfluenceEvent(db.Model):
    """An instance of a User experiencing an Influence."""

    __tablename__ = "influence_events"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    influence_id = db.Column(db.Integer, db.ForeignKey("influences.id"))
    intensity = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    user = db.relationship("User", uselist=False, backref="influence_events")
    influence = db.relationship("Influence", uselist=False, 
                                backref="influence_events")

    def __str__(self):
        """Show Influence id, label, and associated User's username."""

        return f"<InfluenceEvent {self.id} {self.influence.label} "\
               f"{self.user.username}>"    


class Symptom(db.Model):
    """A measurement of one aspect of a User's wellness."""

    __tablename__ = "symptoms"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    label = db.Column(db.String(50), nullable=False)
    scale = db.Column(db.String(20))     # nullable

    def __str__(self):
        """Show Symptom id, label, and associated User's username."""

        return f"<Symptom {self.id} {self.label} {self.user.username}>"


class SymptomEvent(db.Model):
    """An instance of a User experiencing a Symptom."""

    __tablename__ = "symptom_events"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    symptom_id = db.Column(db.Integer, db.ForeignKey("symptoms.id"))
    intensity = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    user = db.relationship("User", uselist=False, backref="symptom_events")
    symptom = db.relationship("Symptom", uselist=False,
                              backref="symptom_events")

    def __str__(self):
        """Show Symptom id, label, and associated User's username."""

        return f"<SymptomEvent {self.id} {self.symptom.label} "\
               f"{self.user.username}>"


class Goal(db.Model):
    """A user-set goal: to do a Habit x times during x time period."""

    __tablename__ = "goals"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    habit_id = db.Column(db.Integer, db.ForeignKey("habits.id"))
    num_units = db.Column(db.Float, nullable=False)
    time_period = db.Column(db.Interval, nullable=False)

    user = db.relationship("User", uselist=False, backref="goals")
    habit = db.relationship("Habit", uselist=False, backref="goals")

    def __str__(self):
        """Show Goal id, associated Habit label, and associated username."""

        return f"<Goal {self.id} {self.habit.label} {self.user.username}>"
