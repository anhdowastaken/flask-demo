from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	isAdmin = BooleanField('Is Admin?')
	submit = SubmitField('Login')

class UploadLicenseForm(FlaskForm):
	licenseFile = FileField('License File', validators=[FileRequired()])
	submit = SubmitField('Upload')