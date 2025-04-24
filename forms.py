from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class ScheduleForm(FlaskForm):
    ewaste_type = SelectField('E-waste Type', choices=[
        ('Laptop', 'Laptop'),
        ('Smartphone', 'Smartphone'),
        ('Desktop-PC', 'Desktop Computer'),
        ('Tablet', 'Tablet'),
        ('Flat-Panel-Monitor', 'Flat Panel Monitor'),
        ('CRT-Monitor', 'CRT Monitor'),
        ('Printer', 'Printer'),
        ('Air-Conditioner', 'Air Conditioner'),
        ('Washing-Machine', 'Washing Machine'),
        ('Refrigerator', 'Refrigerator'),
        ('Microwave', 'Microwave'),
        ('Flat-Panel-TV', 'Flat Panel TV'),
        ('CRT-TV', 'CRT TV'),
        ('Camera', 'Camera'),
        ('Computer-Keyboard', 'Computer Keyboard'),
        ('Computer-Mouse', 'Computer Mouse'),
        ('Headphone', 'Headphone'),
        ('Battery', 'Battery'),
        ('Other', 'Other E-waste')
    ], validators=[DataRequired()])
    
    model = StringField('Model/Brand (if known)')
    ram = SelectField('RAM (for computers)', choices=[
        ('', 'Not Applicable'),
        ('2GB', '2GB'),
        ('4GB', '4GB'),
        ('8GB', '8GB'),
        ('16GB', '16GB'),
        ('32GB', '32GB'),
        ('64GB+', '64GB or more')
    ])
    
    condition = SelectField('Condition', choices=[
        ('Excellent', 'Excellent - Like New'),
        ('Good', 'Good - Minor Wear'),
        ('Fair', 'Fair - Working but Visible Wear'),
        ('Poor', 'Poor - Heavy Wear or Damaged')
    ], validators=[DataRequired()])
    
    pickup_date = DateTimeField('Pickup Date and Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    pickup_address = TextAreaField('Pickup Address', validators=[DataRequired()])
    submit = SubmitField('Schedule Pickup')

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RewardForm(FlaskForm):
    name = StringField('Reward Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    points_required = IntegerField('Points Required', validators=[DataRequired()])
    reward_type = SelectField('Reward Type', choices=[
        ('Product', 'Product'),
        ('Coupon', 'Coupon'),
        ('Discount', 'Discount')
    ], validators=[DataRequired()])
    stock = IntegerField('Stock', validators=[DataRequired()])
    submit = SubmitField('Add Reward')
