from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from clinic import db, login_manager, app
from flask_login import UserMixin
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import uuid as UUID

@login_manager.user_loader 
def load_user(user_id): 
    return User.query.get(int(user_id))

class Patient(db.Model, UserMixin): 
    __bind_key__ = 'patient'
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True) 
    subid = db.Column(db.String(60), unique=True)
    name = db.Column(db.String(10), nullable=False)
    number = db.Column(db.String(11), nullable=True)   
    gender = db.Column(db.String(2), nullable=True)  
    ID_Card = db.Column(db.String(50), nullable=True) 
    year = db.Column(db.String(50), nullable=True)  
    month = db.Column(db.String(50), nullable=True)
    day = db.Column(db.String(50), nullable=True)
    street = db.Column(db.String(50), nullable=True)  
    create = db.Column(db.DateTime, nullable=False, default=datetime.now)   
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    details = db.relationship('Detail', backref='owner')

class Detail(db.Model, UserMixin): 
    __bind_key__ = 'detail'
    __tablename__ = 'detail'
    id = db.Column(db.Integer, primary_key=True) 
    subid = db.Column(db.String(60))
    Symptom = db.Column(db.String(500), nullable=False)  
    Check_result = db.Column(db.String(500), nullable=False) 
    Preliminary_treatment_plan = db.Column(db.String(500), nullable=False)
    cost = db.Column(db.String(500), nullable=False)
    tag = db.Column(db.String(100), nullable=False) #tag slectfield
    Date_of_diagnosis = db.Column(db.DateTime, nullable=False, default=datetime.now)   
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), unique=True, nullable=False)
    patient = db.relationship('Patient', backref='doctor', lazy=True)  
    details = db.relationship('Detail', backref='user', lazy=True)
    medicines = db.relationship('Medicine', backref='doctor', lazy=True)   

class Medicine(db.Model): 
    __bind_key__ = 'medicine'
    __tablename__ = 'medecine'
    id = db.Column(db.Integer, primary_key=True) 
    Vendor = db.Column(db.String(200), nullable=False)
    Quantity = db.Column(db.String(5), nullable=False) 
    Medicine_name = db.Column(db.String(200), nullable=False) 
    Deadline = db.Column(db.String(200), nullable=False) 
    Price = db.Column(db.String(10), nullable=False) 
    How_to_use = db.Column(db.String(200), nullable=False) 
    time_get = db.Column(db.DateTime, nullable=False, default=datetime.now) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 