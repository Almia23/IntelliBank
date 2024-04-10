from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.schema import ForeignKey

class Employee(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(300), unique=True)
    password = db.Column(db.String(100))
    salary = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime(timezone=True), default=func.now())

class Manager(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(300), unique=True)
    password = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone=True), default=func.now())

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(300), unique=True)
    password = db.Column(db.String(100))
    managedBy = db.Column(db.Integer, ForeignKey("employee.id"))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    
class Currents(db.Model, UserMixin):
    acnum = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, ForeignKey("user.id"))
    balance = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    
class Savings(db.Model, UserMixin):
    acnum = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, ForeignKey("user.id"))
    balance = db.Column(db.Integer, default=0)
    accountType = db.Column(db.Integer, default=1)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    
class Transactions(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    from_ac = db.Column(db.Integer)
    to_ac = db.Column(db.Integer)
    amount = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    
    