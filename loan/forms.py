from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo
from loan.models import User

# ---------------- AUTH ----------------
class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('email', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already taken')

class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('submit')


# ---------------- PROFILE ----------------
class UserProfileForm(FlaskForm):
    # Personal Information
    full_names = StringField('Full Names', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Length(min=2, max=50)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=2, max=50)])
    country = StringField('Country', validators=[DataRequired(), Length(min=2, max=50)])
    location = StringField('Location', validators=[DataRequired(), Length(min=2, max=50)])

    # Financial Information
    savings_category = SelectField(
        "Preferred Savings Category",
        choices=[
            ('weekly', 'Weekly Contribution'),
            ('monthly', 'Monthly Contribution')
        ],
        validators=[DataRequired()]
    )

    payment_level = SelectField(
        "Payment Level",
        choices=[
            ('1', 'Level 1 - KSh 100'),
            ('2', 'Level 2 - KSh 200'),
            ('3', 'Level 3 - KSh 300'),
            ('4', 'Level 4 - KSh 400'),
            ('5', 'Level 5 - KSh 500')
        ],
        validators=[DataRequired()]
    )

    goals = TextAreaField('Financial Goals / Notes')  # Optional

    submit = SubmitField('Save Profile')


# ---------------- CONTRIBUTIONS ----------------
class ContributionForm(FlaskForm):
    amount = IntegerField("Amount (KES)", validators=[DataRequired()])
    transaction_code = StringField("MPESA Transaction Code", validators=[DataRequired(), Length(min=5)])
    submit = SubmitField("Submit Contribution")

# ---------------- LOANS ----------------
class LoanApplicationForm(FlaskForm):
    amount = IntegerField("Loan Amount", validators=[DataRequired()])
    purpose = TextAreaField("Loan Purpose", validators=[DataRequired()])
    submit = SubmitField("Apply for Loan")
