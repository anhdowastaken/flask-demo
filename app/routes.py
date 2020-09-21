from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app.forms import LoginForm
from app.models import User, role_required

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
			return redirect(url_for('index'))

	return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
	# Use flash_login to logout
	logout_user()
	return redirect(url_for('index'))
