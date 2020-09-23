from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_apscheduler import APScheduler
import os
import logging

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# migrate = Migrate(app, db, render_as_batch=True)
login = LoginManager(app)
login.login_view = 'login'

if os.environ.get('FLASK_ENV') == 'development':
	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
else:
	logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

from app import routes, models

scheduler = APScheduler()
@scheduler.task('cron', id='check_expired_license', minute='*')
def check_expired_license():
	ls = models.License.query.all()
	logging.info('Number of licenses = {}'.format(len(ls)))

# Avoid running job twice in debug mode
# https://www.tfzx.net/article/2758814.html
if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
	scheduler.init_app(app)
	scheduler.start()