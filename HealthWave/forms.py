from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone Number', validators=[Length(max=20)])
    role = SelectField('Role', choices=[('patient', 'Patient'), ('doctor', 'Doctor')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class AppointmentForm(FlaskForm):
    doctor_id = SelectField('Doctor', coerce=int, validators=[DataRequired()])
    appointment_date = DateTimeField('Appointment Date & Time', validators=[DataRequired()])
    appointment_type = SelectField('Appointment Type', choices=[
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow-up'),
        ('check_up', 'Check-up'),
        ('emergency', 'Emergency')
    ], validators=[DataRequired()])
    notes = TextAreaField('Additional Notes')
    submit = SubmitField('Schedule Appointment')

class AIAnalysisForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    analysis_type = SelectField('Analysis Type', choices=[
        ('cancer_detection', 'Cancer Detection'),
        ('xray_analysis', 'X-Ray Analysis'),
        ('mri_scan', 'MRI Scan Analysis'),
        ('ct_scan', 'CT Scan Analysis')
    ], validators=[DataRequired()])
    image_file = FileField('Medical Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'dcm'], 'Only image files are allowed!')
    ])
    submit = SubmitField('Analyze Image')

class ChatbotForm(FlaskForm):
    message = TextAreaField('Your Message', validators=[DataRequired()], render_kw={"placeholder": "Ask a medical question..."})
    submit = SubmitField('Send')
