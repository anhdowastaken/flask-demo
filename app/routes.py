from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
	return render_template('base.html', title='Index')

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		flash('Login requested for user {}, is-admin={}'.format(form.username.data, form.isAdmin.data))
		return redirect(url_for('index'))
	return render_template('login.html', title='Login', form=form)