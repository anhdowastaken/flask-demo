from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
import logging

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

if os.environ.get('FLASK_ENV') == 'development':
	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
else:
	logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

from app import routes, models

def checkAdmin():
	from app.models import User

	adminUsers = User.query.filter_by(role='admin').all()
	# Delete all admin users if number of admin users is greater than 1
	if len(adminUsers) > 1:
		app.logger.info('There are {} admin users in database'.format(len(adminUsers)))
		app.logger.info('All of them will be deleted')
		for u in adminUsers:
			db.session.delete(u)
			db.session.commit()
	
	# Add admin user if necessary
	if len(adminUsers) != 1:
		app.logger.info('Add new admin user with default password 1')
		u = User(username='admin', role='admin')
		u.set_password('1')
		db.session.add(u)
		db.session.commit()

checkAdmin()