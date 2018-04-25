from datetime import datetime
from flask import Flask, request, redirect, render_template, session, flash, url_for
from werkzeug.utils import secure_filename
from hashutils import make_pw_hash, check_pw_hash
from app import app, db
from models import Blog, User
import os


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

#@app.before_request
#def require_login():
#    allowed_routes = ['login', 'register', 'static']
#    if not ('username' in session or request.endpoint in allowed_routes):
#        return redirect("/login")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username,password)
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect or user does not exist', 'error')
            return redirect('/signup')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's password

        existing_user = User.query.filter_by(username=username).first()
        print("Existing user: ",existing_user)

        if not existing_user:
            print("No existing user")
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

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    return render_template('singleUser.html')

@app.route('/logout')
def logout():
    try:
        del session['username']
        return redirect('/login')
    except ValueError:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():

    return render_template('blog.html')

if __name__ == '__main__':
    app.run(host= '0.0.0.0')
