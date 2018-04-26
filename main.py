from flask import Flask, request, redirect, render_template, session, flash, url_for
from werkzeug.utils import secure_filename
from app import app, db
from models import Blog, User
import os
from hashutils import make_pw_hash, check_pw_hash
import datetime

def get_owner_id():
    user = User.query.filter_by(username=session['username']).first()
    return user.id

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
    allowed_routes = ['login', 'signup', 'static']
    if not ('username' in session or request.endpoint in allowed_routes):
        return redirect("/login")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username,password)
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        elif not user:
            flash('That user does not exist', 'error')
            return redirect('/login')
        else:
            flash('User password incorrect or user does not exist', 'error')
            return redirect('/login')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if not password == verify:
            flash('Those password do not match', 'error')
            return redirect('/signup')
        if len(password)<2 or len(verify)<2:
            flash('Usernames and passwords must be at least 3 characters long', 'error')
            return redirect('/signup')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            flash('User already exists', 'error')
            return redirect('/signup')

    return render_template('signup.html')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    date = str(today())
    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']
        date = request.form['date']

        if title == '':
            flash('Title is required', 'error')
            return render_template('newpost.html', content=content, date=date)
        if content == '':
            flash('That post had no content', 'error')
            return render_template('newpost.html', title=title, date=date)
        else:
            new_blog = Blog(title, content, sql_date_format(date), get_owner_id())
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id=' + str(new_blog.id))

    return render_template('newpost.html', date=date)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method == 'GET':
        if 'id' in request.args:
            blog_id = int(request.args.get('id'))
            blog = Blog.query.join(User).add_columns(User.id, User.username, User.avatar, Blog.title, Blog.content, Blog.date).filter(Blog.id==blog_id).first()
            return render_template('article.html', blog=blog)
        if 'user' in request.args:
            user = request.args.get('user')
            blog = Blog.query.join(User).add_columns(User.id, User.username, User.avatar, Blog.title, Blog.content, Blog.date).filter(User.username==user).order_by(Blog.date.desc()).all()
            return render_template('singleUser.html', blog=blog, username=user)
        else:
            blog = Blog.query.join(User).add_columns(Blog.id, User.id, User.username, User.avatar, Blog.title, Blog.content, Blog.date).order_by(Blog.date.desc()).all()
            return render_template('blog.html', blog=blog)

@app.route('/logout')
def logout():
    try:
        del session['username']
        return redirect('/blog')
    except ValueError:
        return redirect('/blog')

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        user = User.query.all()
        return render_template('index.html', user=user)

if __name__ == '__main__':
    app.run(host= '0.0.0.0')
