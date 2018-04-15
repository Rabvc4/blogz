from datetime import datetime
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import datetime

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = './static/images'

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Review(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    review = db.Column(db.String(120), nullable=False)
    food = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))

    def __init__(self, title, content, review, food, rating, date, restaurant):
        self.title = title
        self.content = content
        self.review = review
        self.food = food
        self.rating = rating
        self.date = date
        self.restaurant_id = restaurant

    def __repr__(self):
        return '<Review %r>' % self.title

class Restaurant(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    image = db.Column(db.String(2048))
    reviews = db.relationship('Review', backref='restaurant')

    def __init__(self, name, image):
        self.name = name
        self.image = image

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_date(date):
    format = '%m-%d-%Y'
    new_format = '%Y-%m-%d'
    date = datetime.datetime.strptime(date, format).strftime(new_format)
    return date

def today():
    now = datetime.datetime.now()
    date = now.strftime("%m-%d-%Y")
    return str(date)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    date = str(today())
    if request.method == 'POST':
        name = request.form['name']
        if 'file' not in request.files:
            flash('No file found', 'error')
            return redirect('/newpost')
        image = request.files['file']
        title = request.form['title']
        content = request.form['content']
        review = request.form['review']
        food = request.form['food']
        rating = request.form['rating']
        date = convert_date(request.form['date'])

        if name == '':
            flash('Restaurant name is required', 'error')
            return redirect('/newpost')
        if image.filename == '':
            flash('No selected image', 'error')
            return redirect('/newpost', name=name)
        if image and not allowed_file(image.filename):
            flash('That image format is not supported')
            return redirect('/newpost')

        existing_restaurant = Restaurant.query.filter_by(name=name).first()
        if not existing_restaurant:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Successfully uploaded:' + filename)
            new_restaurant = Restaurant(name, filename)
            db.session.add(new_restaurant)
            db.session.commit()
            new_restaurant = Restaurant.query.filter_by(name=name).first()
            new_review = Review(title, content, review, food, rating, date, new_restaurant.id)
            db.session.add(new_review)
            db.session.commit()
            return redirect('/blog')
        else:
            flash('Restaurant already exists')
            new_review = Review(title, content, review, food, rating, date, existing_restaurant.id)
            db.session.add(new_review)
            db.session.commit()

    return render_template('newpost.html', date=date)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    date = today()

    if request.method == 'POST':
        submitted_date = request.form['date']
        date = convert_date(submitted_date)
        return render_template('upload.html', date=date)

    return render_template('upload.html', date=date)

@app.route('/blog', methods=['POST', 'GET'])
def index():

    if request.method == 'GET':
        blog = Review.query.all()
        restaurants = Restaurant.query.all()

    return render_template('blog.html', blog=blog, restaurants=restaurants)

if __name__ == '__main__':
    app.run(host= '0.0.0.0')
