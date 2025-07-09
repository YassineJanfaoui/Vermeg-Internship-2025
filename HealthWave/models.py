from datetime import datetime
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')  # 'doctor' or 'patient'
    phone = db.Column(db.String(20))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    doctor_appointments = db.relationship(
        'Appointment',
        foreign_keys='Appointment.doctor_id',
        backref='doctor_user',
        lazy='dynamic'
    )
    
    patient_appointments = db.relationship(
        'Appointment',
        foreign_keys='Appointment.patient_id',
        backref='patient_user',
        lazy='dynamic'
    )
    
    medical_records = db.relationship(
        'MedicalRecord',
        foreign_keys='MedicalRecord.patient_id',
        backref='record_patient',
        lazy='dynamic'
    )
    
    patient_ai_analyses = db.relationship(
        'AIAnalysis',
        foreign_keys='AIAnalysis.patient_id',
        backref='analysis_patient',
        lazy='dynamic'
    )
    
    doctor_ai_analyses = db.relationship(
        'AIAnalysis',
        foreign_keys='AIAnalysis.analyzed_by',
        backref='analysis_doctor',
        lazy='dynamic'
    )
    chat_conversations = db.relationship(
        'ChatConversation',
        backref='chat_user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_doctor(self):
        return self.role == 'doctor'
    
    def is_patient(self):
        return self.role == 'patient'
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    appointment_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Appointment {self.id}: {self.appointment_date}>'

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    record_type = db.Column(db.String(50), nullable=False)  # diagnosis, treatment, test_result
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow)
    doctor_notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<MedicalRecord {self.id}: {self.title}>'

class AIAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)  # cancer_detection, xray_analysis, etc.
    image_filename = db.Column(db.String(200))
    image_type = db.Column(db.String(250))
    result = db.Column(db.Text)  # JSON string with analysis results
    confidence_score = db.Column(db.Float)
    risk_level = db.Column(db.String(20))  # low, medium, high
    recommendations = db.Column(db.Text)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyzed_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # doctor who requested analysis
    patient = db.relationship('User', foreign_keys=[patient_id], backref='analyses_as_patient')
    doctor = db.relationship('User', foreign_keys=[analyzed_by], backref='analyses_as_doctor')
    def __repr__(self):
        return f'<AIAnalysis {self.id}: {self.analysis_type}>'
    
class ChatConversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    is_file = db.Column(db.Boolean, default=False)
    file_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='chat_conversations')
    
    def __repr__(self):
        return f'<ChatConversation {self.id}: {self.role}>'
