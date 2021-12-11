from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta
from clinic import app, db
from clinic.models import User, Detail, Patient, Medicine
from clinic.forms import PatientForm, MedicineForm, DetailForm, UpdateDoctorForm, AddannouncementForm, RequestResetForm, ResetPasswordForm, ChangePatientForm
import uuid
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
import pandas as pd
import base64
from io import BytesIO
from matplotlib.figure import Figure
import os
from dateutil.parser import parse

admin = Admin(app, name="管理员")
admin.add_view(ModelView(User, db.session, name="大夫")) 
admin.add_view(ModelView(Patient, db.session, name="PATIENT")) 
admin.add_view(ModelView(Detail, db.session, name="detail")) 
admin.add_view(ModelView(Medicine, db.session, name='b'))

@app.route("/logout") 
def logout(): 
    logout_user() 
    return redirect(url_for('login'))   

@app.route('/', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        user = db.session.query(User.name).first()
        return redirect(url_for('doctor_information', name=user.name))
    if request.method == 'POST':
        user = request.form.get('user')
        password = request.form.get('password')
        user = User.query.filter_by(name=user).first()
        if user and user.password == password:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('doctor_information', name=user.name))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login')

@app.route("/home-for/<string:name>", methods=['POST', 'GET'])
@login_required 
def doctor_information(name):
    user = User.query.filter_by(name=name).first_or_404()
    # Total new patient
    amount_patient = len(db.session.query(Patient.name).all())
    # Total patient
    mylist = db.session.query(Patient.name).all() 
    mylist1 = len(list(dict.fromkeys(mylist))) # remove duplicate and use len() to count the total patient
    # Total patient for 4 weeks
    current_time = datetime.now() 
    time = timedelta(weeks = 4) 
    four_weeks_ago = current_time - time 
    filter_by_month = db.session.query(Patient.name).filter(Patient.create > four_weeks_ago).all() # filter by the patient during this 4 weeks
    filter_by_month_1 = len(list(dict.fromkeys(filter_by_month))) 
    # Total patient for today
    time_1 = timedelta(days = 1) # filter last 4 weeks
    today = current_time - time_1 # start the counter 
    #filter_by_today = db.session.query(Patient.name).filter(Patient.create > today).all() # filter by the patient during this 4 weeks 
    filter_by_today_1 = PatientData.AmountPatientToday()
    # Money spent

    today = current_time - time_1 # start the counter 
    Money_today = [float(str(i)[2:-3]) for i in db.session.query(Medicine.Price).filter(Medicine.time_get > today).all()] # filter by the patient during this 4 weeks
    Money_today_1 = sum(Money_today)

    time = timedelta(weeks = 4) 
    four_weeks_ago = current_time - time 
    Money_month = [float(str(i)[2:-3]) for i in db.session.query(Medicine.Price).filter(Medicine.time_get > four_weeks_ago).all()]
    Money_month_1 = sum(Money_month)
    # Money earn

    #Money_earn_today = [float(str(i)[2:-3]) for i in db.session.query(Detail.cost).filter(Detail.Date_of_diagnosis > today).all()]
    Money_earn_today_1 = 0

    four_weeks_ago = current_time - time 
    #Money_earn_month = [float(str(i)[2:-3]) for i in db.session.query(Detail.cost).filter(Detail.Date_of_diagnosis > four_weeks_ago).all()]
    #Money_earn = [float(str(i)[2:-3]) for i in db.session.query(Detail.drip).filter(Detail.Date_of_diagnosis > four_weeks_ago).all()]
    Money_earn_month_1 = 0
    return render_template('main.html', user=user, mylist1=mylist1, amount_patient=amount_patient, 
    filter_by_month_1=filter_by_month_1, filter_by_today_1=filter_by_today_1, Money_today_1=Money_today_1, Money_month_1=Money_month_1,
    Money_earn_1=Money_earn_today_1, Money_earn_month_1=Money_earn_month_1)    

@app.route("/patient") 
@login_required 
def patient(): 
    page = request.args.get('page', 1, type=int) # get all the posts from db file
    patients = Patient.query.order_by(Patient.create.desc()).paginate(page=page, per_page=15) # posts were order by date, 20 posts each page
    return render_template('patient.html', patients=patients)

PatientDictionary = {}
datarefreshLog = []

def converter(date: str) -> str:
    if date[-1] == ',':
        date = date[:-1]
        return tuple(int(item) for item in date.split(', '))
    else:
        return tuple(int(item) for item in date.split(', '))

class PatientData():
    def __init__(self, subid: str, create: str) -> str:
        self.self = self
        self.subid = subid
        self.create = create

    def converter1(self, date: str) -> str:
        return tuple(int(item) for item in date.split('-'))
    
    def DatabaseToDictionary(self):
        arr = list(zip(self.create, self.subid))   
        for create, subid in arr:
            if create in PatientDictionary.keys():
                PatientDictionary[create].append(subid)
            else:
                PatientDictionary[create] = [] # create empty list for new key
                PatientDictionary[create].append(subid)

    def save_data(self): # save to csv
        arr = {'date':[],'patient':[], 'count':[]}
        for key in PatientDictionary.keys():
            arr['date'].append(key) # patient create date
            arr['patient'].append(PatientDictionary[key]) # patient subid
            arr['count'].append(len(PatientDictionary[key])) # amount patient
        df = pd.DataFrame(arr, columns= ['date','patient', 'count'])
        df.to_csv('patient.csv', index = True, header=True)
    
    def dataLogfunc():
        now = datetime.now()
        datarefreshLog.append(str(now)[11:13])

    def refreshDictdata():
        now = datetime.now()
        if int(str(now)[11:13]) - int(datarefreshLog[-1]) >= 2:
            PatientData.data()
        else:
            pass

    def AmountPatientToday(self):
        now = PatientData.converter1(str(datetime.now())[:10])
        try:
            return len(PatientDictionary[now]) 
        except KeyError: 
            PatientData.DatabaseToDictionary()
            return 0

PatientData = PatientData([str(i)[2:-3] for i in db.session.query(Patient.subid)], [converter(str(i)[19:31]) for i in db.session.query(Patient.create)])
PatientData.DatabaseToDictionary()
print(PatientDictionary)
token = uuid.uuid4()
token_dict = []
token_dict.append(token)
log = {}

@app.route('/clinic-admin', methods=['GET','POST'])
@login_required
def clinic_admin():
    if request.method == 'POST':
        user = request.form.get('user')
        password = request.form.get('password')
        if user == 'admin' and password == '123':
            now = datetime.now()
            log[str(now)[11:13]] = user
            return redirect('/clinic-admin/%s' % token_dict[-1])
    return render_template('login.html')

@app.route('/clinic-admin/%s' % token_dict[-1], methods=['GET','POST'])
@login_required
def clinic_admin_page():
    now = datetime.now()
    time = [i for i in log.keys()]
    if int(str(now)[11:13]) - int(time[-1]) > 8:
        return redirect('/clinic-admin')
    fig = Figure()
    data = pd.read_csv('patient.csv')
    ax = fig.subplots()
    x = data['date']
    y = data['count']
    ax.plot(x, y)
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return render_template("clinic_admin_page.html", image=data)

a = uuid.uuid4()
def checkValidsubId(subid: str) -> str: # subid should be unique value
    Allsubid = list(db.session.query(Patient.subid))
    while subid in Allsubid:
        subid = uuid.uuid4()
        return subid.hex
    return subid

@app.route("/addpatient", methods=['GET', 'POST']) 
@login_required 
def addpatient(): 
    form = PatientForm() 
    if form.validate_on_submit(): 
        patient1 = Patient(name=form.name.data, number=form.number.data, gender=form.gender.data, ID_Card=form.ID_Card.data, street=form.street.data)   
        ID = (patient1.ID_Card) 
        subid = checkValidsubId(a.hex)
        patient = Patient(subid=subid, name=form.name.data, number=form.number.data, gender=form.gender.data, ID_Card=form.ID_Card.data, 
        year = ID[slice(6,10)], month = ID[slice(10, 12)], day = ID[slice(12, 14)], street=form.street.data, doctor=current_user)   
        db.session.add(patient) 
        db.session.commit()
        PatientData.save_data()
        now = PatientData.converter1(str(datetime.now())[:10])
        PatientDictionary[now].append(subid)
        time = datetime.now()
        day = time.strftime("%A") 
        date = day[:3] 
        file = open('log.txt','a')
        file.writelines('%s %s/%s/%s 患者："%s" 个人信息已被医生："%s" 加入进数据库.\n' % (date, time.month, time.day, time.year, patient.name, patient.doctor.name))
        file.close()
        flash('此患者已被加入进数据库当中', 'success') 
        return redirect(url_for('patient')) 
    return render_template('add-patient.html', title='Add Patient', form=form) 

@app.route("/patient/<string:subid>") 
@login_required
def patient_subid(subid): 
    patient = Patient.query.filter_by(subid=subid).first_or_404()
    return render_template('patient_info.html', patient=patient)  

@app.route("/update-patient/<string:subid>", methods=['GET', 'POST'])  
@login_required 
def update_patient(subid):
    patient = Patient.query.filter_by(subid=subid).first_or_404()
    form = ChangePatientForm() 
    if form.validate_on_submit(): 
        patient.number = form.number.data 
        patient.street = form.street.data
        db.session.commit()
        time = datetime.now()
        day = time.strftime("%A")
        date = day[:3] 
        file = open('log.txt','a')
        file.writelines('%s %s/%s/%s 患者："%s" 个人信息被医生："%s" 更改.\n' % (date, time.month, time.day, time.year, patient.name, patient.doctor.name))
        file.close()
        flash('患者信息已更改!', 'success') 
        return redirect(url_for('patient_info', name=patient.name))
    elif request.method == 'GET':
        form.number.data = patient.number
        form.street.data = patient.street
    return render_template('change-patient.html', title='Update Patient',
                           form=form, legend='Update Patient') 

@app.route("/delete-patient/<string:subid>", methods=['GET', 'POST']) 
@login_required
def delete_patient(subid): 
    patient = Patient.query.filter_by(subid=subid).first_or_404()
    detail = Patient.query.filter_by(subid=subid).first_or_404()
    if patient.id == detail.id: 
        db.session.delete(detail) 
        db.session.delete(patient) 
        db.session.commit() 
        flash('此患者已被删除')
    elif detail.id not in patient.id:
        db.session.delete(patient)
        db.session.commit() 
        flash('此患者已被删除')
    now = PatientData.converter1(str(datetime.now())[:10])
    PatientDictionary[now].remove(str(subid))
    time = datetime.now()
    day = time.strftime("%A")
    date = day[:3] 
    file = open('log.txt','a')
    file.writelines('%s %s/%s/%s 患者："%s" 个人/病患信息已被医生："%s" 删除.\n' % (date, time.month, time.day, time.year, patient.name, patient.doctor.name))
    file.close()
    return redirect(url_for('patient')) 

@app.route("/patient-info/<string:name>") 
@login_required
def patient_info(name): 
    patient = Patient.query.filter_by(name=name).first_or_404()
    return render_template('patient_info.html', patient=patient)    

@app.errorhandler(404)
def not_found(e):
  return render_template('custom_page.html'), 404

@app.route("/patient-detail/<string:subid>", methods=['GET', 'POST']) 
@login_required 
def patientdetail(subid): 
    patient = Patient.query.filter_by(subid=subid).first_or_404()
    detail = Detail.query.filter_by(subid=subid).first_or_404()
    return render_template('patient_detail.html', detail=detail, patient=patient)

symptom_suggestion = {}

def stat(form):
    symptom = db.session.query(Detail.Symptom) # factor
    result = db.session.query(Detail.Check_result) # result
    for res in result:
        for sym in symptom: 
            symptom_suggestion[sym] = res
    while len(symptom_suggestion) > 10:
        for k in symptom_suggestion.keys():
            if form[0] in k:
                return str(symptom_suggestion[k])
    else:
        return form[1]

arr = {'symptom': [], 'patient': []}
@app.route("/add-patient-detail/<string:subid>", methods=['GET', 'POST']) 
@login_required  
def add_patient_detail(subid): 
    form = DetailForm()   
    if form.validate_on_submit():  
        patient = Patient.query.filter_by(subid=subid).first_or_404()  
        detail = Detail(subid=patient.subid, Symptom=form.Symptom.data, Check_result=form.Check_result.data, 
        Preliminary_treatment_plan=form.Preliminary_treatment_plan.data, cost=form.cost.data, tag=stat([form.Symptom.data, form.Check_result.data]), user=current_user, owner=patient)
        db.session.add(detail) 
        db.session.commit()  
        arr['symptom'].append(detail.tag)
        arr['patient'].append(patient.subid)
        df = pd.DataFrame(arr, columns= ['symptom','patient'])
        df.to_csv('patientSymptom.csv', index = True, header=True)
        time = datetime.now()
        now = str(datetime.now())[:10].replace('-', ', ')
        time1 = tuple(int(item) for item in now.split(', '))
        day = time.strftime("%A")
        date = day[:3] 
        file = open('log.txt','a')
        file.writelines('%s %s/%s/%s 患者："%s" 病患信息已被医生："%s" 加入进数据库.\n' % (date, time.month, time.day, time.year, patient.name, detail.user.name))
        file.close()
        flash('此患者已被加入进数据库当中', 'success') 
        return redirect(url_for('patient'))     
    return render_template('add-patient-detail.html', title='Add Patient Detail', form=form)   

@app.route("/patient-detail-update/<int:patient_id>", methods=['GET', 'POST'])  
@login_required   
def patient_detail_update(patient_id): 
    detail = Detail.query.get_or_404(patient_id)   
    patient = Patient.query.get_or_404(patient_id)
    form = DetailForm()  
    if form.validate_on_submit(): 
        detail.Symptom = form.Symptom.data 
        detail.Check_result = form.Check_result.data 
        detail.Preliminary_treatment_plan = form.Preliminary_treatment_plan.data 
        detail.tag = form.tag.data
        db.session.commit()
        time = datetime.now()
        day = time.strftime("%A")
        date = day[:3] 
        file = open('log.txt','a')
        file.writelines('%s %s/%s/%s 患者："%s" 病患信息已被医生："%s" 更改.\n' % (date, time.month, time.day, time.year, patient.name, detail.user.name))
        file.close()
        flash('患者信息已更改!', 'success') 
        return redirect(url_for('patientdetail', patient_id=detail.id))
    elif request.method == 'GET':
        form.Symptom.data = detail.Symptom
        form.Check_result.data = detail.Check_result
        form.Preliminary_treatment_plan.data = detail.Preliminary_treatment_plan 
        form.tag.data = detail.tag
    return render_template('add-patient-detail.html', title='Update Patient-Detail',
                           form=form, legend='Update Patient-Detail', patient=patient) 
 
@app.route('/medicine', methods=['GET', 'POST'])  
@login_required
def medicine():
    page = request.args.get('page', 1, type=int) # get all the posts from db file
    medicines = Medicine.query.order_by(Medicine.time_get.desc()).paginate(page=page, per_page=10)
    return render_template('medicine.html', medicines=medicines) 
