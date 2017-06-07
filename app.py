from flask import Flask, url_for, redirect, flash, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin, AnonymousUserMixin
# from werkzeug.security import generate_password_hash, check_password_hash
import config as config
import datetime

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"

class User(db.Model, UserMixin):
	__tablename__ = 'admin'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(120), unique=True)
	password = db.Column(db.String(120), unique=True)
	authenticated = db.Column(db.Boolean, default = False)

	def __init__(self, email, password):
		self.email = email
		self.password = password

	def is_active(self):
		"""True, as all users are active."""
		return True

	def get_id(self):
		"""Return the email address to satisfy Flask-Login's requirements."""
		return self.id

	def is_authenticated(self):
		"""Return True if the user is authenticated."""
		return self.authenticated

	def is_anonymous(self):
		return False

class Anonymous(AnonymousUserMixin):
  def __init__(self):
    self.authenticated = False

class Post(db.Model):
	__tablename__ = 'post'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(120), unique = True)
	username = db.Column(db.String(50))
	text = db.Column(db.Text)
	draft = db.Column(db.String(4), default= True)
	date = db.Column(db.DateTime)
	tags = db.Column(db.PickleType)

	def __init__(self, title, username, text, draft, date, tags):
		self.title = title
		self.username = username
		self.text = text
		self.draft = draft
		self.date = date
		self.tags = tags


login_manager.anonymous_user = Anonymous

@login_manager.user_loader
def user_loader(user_id):
	return User.query.get(user_id)


@app.route('/')
def index():
	return render_template("index.html")

@app.route('/admin', methods= ['POST', 'GET'])
def admin():
	if request.method == 'POST':
		email = request.form["inputEmail"]
		password = request.form["inputPassword"]
		user = User.query.filter_by(email = email).first()
		if user is not None:
			if password == user.password:
				user.authenticated = True
				db.session.add(user)
				db.session.commit()
				login_user(user)
				flash("logged in successfully")
				return redirect(url_for('dashboard'))
			else:
				print("wrong password")	
	elif request.method == 'GET':
		if current_user.authenticated:
			return redirect(url_for('dashboard'))
	return render_template('admin.html')

@app.route('/dashboard', methods = ['POST', 'GET'])
@login_required
def dashboard():
	return render_template("dashboard.html")

@app.route('/logout')
@login_required
def logout():
	user = current_user
	user.authenticated = False
	db.session.add(user)
	db.session.commit()
	logout_user()
	return redirect(url_for('index'))

@app.route('/post/<post_status>', methods = ['GET', 'POST'])
@login_required
def post(post_status):
	draft = 'off'
	if request.method == 'POST':
		blog_dict = request.form.to_dict()
		title = blog_dict['title']
		text = blog_dict['text']
		username = blog_dict['username']
		tags = blog_dict['tag']
		post = Post(title, username, text, blog_dict['draft'], datetime.datetime.now(), tags)
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('dashboard'))
	return render_template('blog.html')


if __name__ == '__main__':
	app.run(debug = True)