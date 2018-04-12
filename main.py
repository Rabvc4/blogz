from datetime import datetime
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
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


class Restaurant(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    image = db.Column(db.String(2048))
    reviews = db.relationship('Review', backref='restaurant')

    def __init__(self, name, image):
        self.name = name
        self.image = image


@app.route('/', methods=['POST', 'GET'])
def index():

    return render_template('blog.html', )

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        name = request.form['name']
        image = request.form['image']
        title = request.form['title']
        content = request.form['content']
        review = request.form['review']
        food = request.form['food']
        rating = request.form['rating']
        submitted_date = request.form['date']
        date = datetime.strptime(date, '%Y %b %d')

        # TODO - validate user's data

        existing_restaurant = Restaurant.query.filter_by(name=name).first()
        if not existing_restaurant:
            new_restaurant = Restaurant(name, image)
            db.session.add(new_restaurant)
            db.session.commit()
            new_restaurant = Restaurant.query.filter_by(name=name).first()
            new_review = Review(title, content, review, food, rating, date, new_restaurant.id)
            db.session.add(new_review)
            db.session.commit()
            return redirect('/')
        else:
            flash('Restaurant already exists', 'error')
            new_review = Review(title, content, review, food, rating, date, existing_restaurant.id)
            db.session.add(new_review)
            db.session.commit()

# TODO make correct fields repopulate
    return render_template('newpost.html')

if __name__ == '__main__':
    app.run(host= '0.0.0.0')
