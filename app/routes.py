from flask import render_template, flash, redirect, url_for, send_file
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, UploadLicenseForm
from app.models import User, License, role_required
from io import BytesIO

@app.route('/')
@app.route('/index')
# Authenticated user is required to access index
@login_required
def index():
	return render_template('index.html', title='Index')

@app.route('/admin')
@login_required
@role_required('admin')
def admin():
	return render_template('admin.html', title='Admin')

@app.route('/sale')
@login_required
@role_required('sale')
def sale():
	form = UploadLicenseForm()
	licenseFiles = License.query.all()

	return render_template('sale.html', title='Sale', licenseFiles=licenseFiles, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	# If current user is authenticated, redirect to index
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = LoginForm()
	if form.validate_on_submit():
		if form.isAdmin.data:
			# If user is admin, filter role='admin'
			user = User.query.filter_by(username=form.username.data, role='admin').first()
		else:
			# To allow !=, use filter() instead of filter_by()
			user = User.query.filter(User.username == form.username.data, User.role != 'admin').first()

		# Check password
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))

		# Use flash_login to login
		login_user(user)

		if form.isAdmin.data:
			return redirect(url_for('admin'))
		else:
			if user.role == 'sale':
				return redirect(url_for('sale'))
			return redirect(url_for('index'))

	return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
	# Use flash_login to logout
	logout_user()
	return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
@login_required
@role_required('sale')
def upload():
	form = UploadLicenseForm()
	if form.validate_on_submit():
		f = form.licenseFile.data
		licenseFile = License(content=f.read())
		licenseFile.user_id = current_user.id
		db.session.add(licenseFile)
		db.session.commit()

	return redirect(url_for('sale'))

@app.route('/download/<license_id>', methods=['GET'])
@login_required
@role_required('sale')
def download(license_id):
	licenseFile = License.query.filter_by(id=license_id).first()
	if licenseFile:
		return send_file(BytesIO(licenseFile.content), attachment_filename='license', as_attachment=True)
	else:
		flash('License file is unavailable')
		return redirect(url_for('sale'))