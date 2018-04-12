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
    title = db.Column(db.String(120))
    content = db.Column(db.String(1000))
    review = db.Column(db.String(120))
    food = db.Column(db.String(120))
    rating = db.Column(db.Integer)
    date = db.Column(DateTime, default=datetime.datetime.utcnow)
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
    name = db.Column(db.String(120))
    image = db.Column(db.String(2048))
    reviews = db.relationship('Review', backref='restaurant')

    def __init__(self, name, image):
        self.name = name
        self.image = image


@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        task_name = request.form['review']
        new_task = Task(task_name, owner)
        db.session.add(new_task)
        db.session.commit()

    tasks = Task.query.filter_by(completed=False,owner=owner).all()
    completed_tasks = Task.query.filter_by(completed=True,owner=owner).all()
    return render_template('todos.html',title="Get It Done!",
        tasks=tasks, completed_tasks=completed_tasks)

if __name__ == '__main__':
    app.run(host= '0.0.0.0')
