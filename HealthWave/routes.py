import os
import json
import random
from datetime import datetime, timedelta
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from services import cancer_service
from models import User, Appointment, MedicalRecord, AIAnalysis
from forms import LoginForm, RegistrationForm, AppointmentForm, AIAnalysisForm, ChatbotForm
from app import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_doctor():
            return redirect(url_for('doctor_dashboard'))
        else:
            return redirect(url_for('patient_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        
        login_user(user)
        flash(f'Welcome back, {user.get_full_name()}!', 'success')
        
        if user.is_doctor():
            return redirect(url_for('doctor_dashboard'))
        else:
            return redirect(url_for('patient_dashboard'))
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    print(f"Form submitted: {form.is_submitted()}")  # Debug
    print(f"Form validated: {form.validate_on_submit()}")  # Debug
    
    if form.validate_on_submit():
        print("Form validation passed")  # Debug
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('index'))
    
    print(f"Form errors: {form.errors}")  
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


#Doctor
@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if not current_user.is_doctor():
        flash('Access denied. Doctor privileges required.', 'error')
        return redirect(url_for('index'))
    
    recent_appointments = Appointment.query.filter_by(doctor_id=current_user.id).order_by(Appointment.appointment_date.desc()).limit(5).all()
    
    recent_analyses = AIAnalysis.query.filter_by(analyzed_by=current_user.id).order_by(AIAnalysis.analyzed_at.desc()).limit(5).all()
    
    return render_template('doctor/dashboard.html', 
                         recent_appointments=recent_appointments,
                         recent_analyses=recent_analyses)

@app.route('/doctor/ai-analysis', methods=['GET', 'POST'])
@login_required
def ai_analysis():
    if not current_user.is_doctor():
        flash('Access denied. Doctor privileges required.', 'error')
        return redirect(url_for('index'))
    
    form = AIAnalysisForm()
    form.patient_id.choices = [(p.id, f"{p.get_full_name()} ({p.username})") 
                             for p in User.query.filter_by(role='patient').all()]
    
    if form.validate_on_submit():
        try:
            analysis_data = cancer_service.analyze_image(
                form.image_file.data,
                form.patient_id.data,
                current_user.id
            )
            
            analysis = AIAnalysis(**analysis_data)
            db.session.add(analysis)
            db.session.commit()
            
            flash(f'{analysis_data["analysis_type"]} completed!', 'success')
            return redirect(url_for('ai_analysis'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Analysis error: {str(e)}', 'error')
            app.logger.error(f"Cancer analysis failed: {str(e)}")

    analyses = AIAnalysis.query.filter_by(analyzed_by=current_user.id)\
                             .order_by(AIAnalysis.analyzed_at.desc())\
                             .limit(10).all()
    return render_template('doctor/ai_analysis.html', form=form, analyses=analyses)

@app.route('/doctor/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot():
    if not current_user.is_doctor():
        flash('Access denied. Doctor privileges required.', 'error')
        return redirect(url_for('index'))
    
    form = ChatbotForm()
    response = None
    
    if form.validate_on_submit():
        message = form.message.data.lower()
    
    return render_template('doctor/chatbot.html', form=form, response=response)

@app.route('/doctor/3d-viewer')
@login_required
def viewer_3d():
    if not current_user.is_doctor():
        flash('Access denied. Doctor privileges required.', 'error')
        return redirect(url_for('index'))
    
    return render_template('doctor/viewer_3d.html')

@app.route('/doctor/patients')
@login_required
def patients():
    if not current_user.is_doctor():
        flash('Access denied. Doctor privileges required.', 'error')
        return redirect(url_for('index'))
    
    patients = User.query.filter_by(role='patient').all()
    return render_template('doctor/patients.html', patients=patients)

# Patient
@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if not current_user.is_patient():
        flash('Access denied. Patient privileges required.', 'error')
        return redirect(url_for('index'))
    
    upcoming_appointments = Appointment.query.filter_by(patient_id=current_user.id).filter(
        Appointment.appointment_date > datetime.now()
    ).order_by(Appointment.appointment_date.asc()).limit(5).all()
    
    recent_records = MedicalRecord.query.filter_by(patient_id=current_user.id).order_by(
        MedicalRecord.date_recorded.desc()
    ).limit(5).all()
    
    return render_template('patient/dashboard.html', 
                         upcoming_appointments=upcoming_appointments,
                         recent_records=recent_records)

@app.route('/patient/history')
@login_required
def patient_history():
    if not current_user.is_patient():
        flash('Access denied. Patient privileges required.', 'error')
        return redirect(url_for('index'))
    
    appointments = Appointment.query.filter_by(patient_id=current_user.id).order_by(
        Appointment.appointment_date.desc()
    ).all()
    
    medical_records = MedicalRecord.query.filter_by(patient_id=current_user.id).order_by(
        MedicalRecord.date_recorded.desc()
    ).all()
    
    ai_analyses = AIAnalysis.query.filter_by(patient_id=current_user.id).order_by(
        AIAnalysis.analyzed_at.desc()
    ).all()
    
    return render_template('patient/history.html', 
                         appointments=appointments,
                         medical_records=medical_records,
                         ai_analyses=ai_analyses)

@app.route('/patient/schedule', methods=['GET', 'POST'])
@login_required
def schedule_appointment():
    if not current_user.is_patient():
        flash('Access denied. Patient privileges required.', 'error')
        return redirect(url_for('index'))
    
    form = AppointmentForm()
    form.doctor_id.choices = [(d.id, f"Dr. {d.get_full_name()}") for d in User.query.filter_by(role='doctor').all()]
    
    if form.validate_on_submit():
        appointment = Appointment(
            doctor_id=form.doctor_id.data,
            patient_id=current_user.id,
            appointment_date=form.appointment_date.data,
            appointment_type=form.appointment_type.data,
            notes=form.notes.data
        )
        db.session.add(appointment)
        db.session.commit()
        
        flash('Appointment scheduled successfully!', 'success')
        return redirect(url_for('patient_dashboard'))
    
    return render_template('patient/schedule.html', form=form)
