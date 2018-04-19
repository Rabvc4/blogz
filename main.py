from datetime import datetime
from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import datetime

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = './static/images'

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = 'dogs'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.Date, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, date, owner):
        self.title = title
        self.content = content
        self.date = date
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % self.title

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(2048), default="avatar.png")
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, username, password, first_name, last_name, avatar, blog):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.avatar = avatar

    def __repr__(self):
        return '<User %r>' % self.username

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sql_date_format(date):
    format = '%m-%d-%Y'
    new_format = '%Y-%m-%d'
    try:
        date = datetime.datetime.strptime(date, format).strftime(new_format)
        return date
    except ValueError:
        return date

def today():
    now = datetime.datetime.now()
    date = now.strftime("%m-%d-%Y")
    return str(date)

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', './static/images']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's password

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            flash('User already exists', 'error')

    return render_template('signup.html')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    date = str(today())
    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        content = request.form['content']
        date = request.form['date']
        if 'file' not in request.files:
            flash('No file found', 'error')
            return render_template('newpost.html', name=name, title=title, content=content, review=review, food=food, rating=rating, date=date)
        image = request.files['file']

        if name == '':
            flash('Restaurant name is required', 'error')
            return render_template('newpost.html', name=name, image=image, content=content, review=review, food=food, rating=rating, date=date)
        if image.filename == '':
            flash('No selected image', 'error')
            return render_template('newpost.html', name=name, content=content, review=review, food=food, rating=rating, date=date)
        if image and not allowed_file(image.filename):
            flash('That image format is not supported')
            return render_template('newpost.html', name=name, content=content, review=review, food=food, rating=rating, date=date)

        if title == '':
            flash('Title is required', 'error')
            return render_template('newpost.html', name=name, image=image, content=content, review=review, food=food, rating=rating, date=date)
        if content == '':
            flash('That post had no content', 'error')
            return render_template('newpost.html', name=name, image=image, title=title, review=review, food=food, rating=rating, date=date)

        existing_restaurant = Restaurant.query.filter_by(name=name).first()
        if not existing_restaurant:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Successfully uploaded:' + filename)
            new_restaurant = Restaurant(name, filename)
            db.session.add(new_restaurant)
            db.session.commit()
            new_restaurant = Restaurant.query.filter_by(name=name).first()
            new_review = Review(title, content, review, food, rating, sql_date_format(date), new_restaurant.id)
            db.session.add(new_review)
            db.session.commit()
            return redirect('/blog')

    return render_template('newpost.html', date=date)

@app.route('/', methods=['POST', 'GET'])
def index():

    return render_template('blog.html')

if __name__ == '__main__':
    app.run(host= '0.0.0.0')
