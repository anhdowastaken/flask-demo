from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import functools
from flask import abort
from flask_login import UserMixin, current_user
from sqlalchemy.orm import validates
from app import db
from app import login

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True, nullable=False)
	password_hash = db.Column(db.String(128))
	role = db.Column(db.Enum('admin', 'sale'), default='sale')
	licenses = db.relationship('License', backref='uploader', lazy='dynamic')

	# This solution below doesn't work
	# because A check constraint cannot contain a subquery (sqlite.org/lang_createtable.html)
	# __table_args__ = (
	# 	db.CheckConstraint('(SELECT COUNT(*) FROM user WHERE role="admin") <= 1'),
	# )
	# Use this instead
	@validates('role')
	def validate_role(self, key, role):
		if not role:
			raise AssertionError('No role provided')

		if User.query.filter_by(role='admin').count() >= 1 and role == 'admin':
			raise AssertionError('Admin already existed')

		return role

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

class License(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	content = db.Column(db.BLOB)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<License {}>'.format(self.timestamp)

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

def role_required(role):
	def decorator(original_route):
		@functools.wraps(original_route)
		def decorated_route(*args, **kwargs):
			if not current_user.is_authenticated:
				abort(401)
			
			if role != current_user.role:
				abort(401, 'Missing role: {}'.format(role))

			return original_route(*args, **kwargs)
		return decorated_route
	return decorator

