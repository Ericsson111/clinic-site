from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from clinic.models import User, Detail, Patient

class DetailForm(FlaskForm):
    Symptom = StringField('Symptom') 
    Check_result = StringField('Check_result')
    Preliminary_treatment_plan = StringField('Preliminary_treatment_plan')
    cost = StringField('cost')
    submit = SubmitField('添加') 

class MedicineForm(FlaskForm):
    Vendor = StringField('Vendor') 
    Quantity = StringField('Quantity') 
    Medicine_name = StringField('Medicine') 
    Price = StringField('Price')
    How_to_use = StringField('How_to_use')
    submit = SubmitField('添加') 

class PatientForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=2, max=20)]) 
    number = StringField('number') 
    gender = SelectField('gender', choices=[('女', '女'), ('男', '男')]) 
    ID_Card = StringField('ID_Card', validators=[DataRequired(), Length(min=2, max=20)])   
    street = StringField('street')  
    submit = SubmitField('添加')  

class ChangePatientForm(FlaskForm):
    number = StringField('number') 
    street = StringField('street')  
    submit = SubmitField('添加')  

class UpdateDoctorForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    number = StringField('number') 
    department = StringField('department')  
    submit = SubmitField('确认')

    def validate_username(self, name):
        user = User.query.filter_by(name=name.data).first() 
        if user:
            raise ValidationError('That name is taken. Please choose a different one.')

class AddannouncementForm(FlaskForm):
    title = StringField('title')
    body = StringField('body')
    submit = SubmitField('发布')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('要求重设密码')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('重设密码')

