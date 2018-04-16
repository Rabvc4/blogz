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

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    date = str(today())
    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        content = request.form['content']
        review = request.form['review']
        food = request.form['food']
        rating = request.form['rating']
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
        else:
            flash('Restaurant already exists')
            new_review = Review(title, content, review, food, rating, sql_date_format(date), existing_restaurant.id)
            db.session.add(new_review)
            db.session.commit()
            return redirect('/blog')


    return render_template('newpost.html', date=date)

@app.route('/blog', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        if 'id' in request.args:
            review_id = int(request.args.get('id'))
            print("FIRST REVIEW ID: ",review_id)
            review = Review.query.join(Restaurant).add_columns(Restaurant.name, Restaurant.image, Review.title, Review.content, Review.food, Review.review, Review.rating, Review.date).filter(Review.id==review_id).first()
            return render_template('review.html', review=review)
        else:
            blog = Review.query.join(Restaurant).add_columns(Review.id, Restaurant.name, Restaurant.image, Review.title, Review.content, Review.food, Review.review, Review.rating, Review.date).order_by(Review.date.desc()).all()
            return render_template('blog.html', blog=blog)

if __name__ == '__main__':
    app.run(host= '0.0.0.0')
