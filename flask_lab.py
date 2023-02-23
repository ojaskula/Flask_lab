from operator import truediv
from pickle import TRUE
from flask import Flask
from flask import render_template, request, redirect, url_for, flash, session
from flask_session import Session
import sqlite3


app = Flask("Flask - Lab")
DATABASE = 'database.db'
sess = Session()


def column(matrix, i):
    return [row[i] for row in matrix]


def is_admin(users):
    if (session['user'] in column(users, 1)) and (users[column(users, 1).index(session['user'])][3] == 1):
        return True
    else:
        return False


def password_check(users, req_form):
    if (req_form['login'] in column(users, 1)) and (users[column(users, 1).index(req_form['login'])][2] == req_form['password']):
        return True
    else:
        return False


def get_users():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("select * from users")
    return cur.fetchall()


def get_books():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("select * from books")
    return cur.fetchall()


def insert_user(login,password,admin):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("select * from users")
    usrs = cur.fetchall()
    id = len(usrs)

    for user in usrs:
        if (user[1] == login):
            con.close()
            return False

    cur.execute("INSERT INTO users (id,username,password,admin) VALUES (?,?,?,?)",(id,login,password,admin) )
    con.commit()
    con.close()
    return True


def insert_book(author,title):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("select * from books")
    books_ = cur.fetchall(); 

    for book in books_:
        if (book[0] == author) and (book[1] == title):
            con.close()
            return False

    cur.execute("INSERT INTO books (author,title) VALUES (?,?)",(author,title) )
    con.commit()
    con.close()
    return True

@app.route('/create_database', methods=['GET', 'POST'])
def create_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute('CREATE TABLE users (id INT, username TEXT, password TEXT, admin INT)')
    conn.execute('CREATE TABLE books (author TEXT, title TEXT)')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (id,username,password,admin) VALUES (?,?,?,?)",(0,'admin','admin',1) )
    conn.commit()
    conn.close()
    
    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' in session:
        return books()
    else:
        return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login(methods=['POST']):
    if request.method == 'POST':
        users = get_users(); 

        req_form = request.form.to_dict()
        if password_check(users, req_form):
            session['user']=req_form['login']
            return books()
        else:
            return "Wrong login or password. <br>" + render_template('login.html')


@app.route('/users', methods=['GET', 'POST'])
def users():
    users = get_users(); 

    if is_admin(users):
        return render_template('users.html', users = users)
    else:
        return "You don't have a permission to view users. <br>" + books()
    

@app.route('/books', methods=['GET', 'POST'])
def books():
    books = get_books()

    return render_template('books.html', books = books)


@app.route('/add-user', methods=['POST'])
def add_user():
    login = request.form['login']
    password = request.form['password']
    admin = 0
    if request.form.get('admin'):
        admin = 1

    if insert_user(login,password,admin):
        return "User succesfully added. <br>" + users()
    else:
        return "User already exists. <br>" + users()


@app.route('/add-book', methods=['POST'])
def add_book():
    author = request.form['author']
    title = request.form['title']
    
    if insert_book(author,title):
        return "Book succesfully added. <br>" + books()
    else:
        return "Book has been already exists. <br>" + books()
    


@app.route('/logout', methods=['GET'])
def logout():
    if 'user' in session:
        session.pop('user')
    else:
        redirect(url_for('login'))
    
    return "Logged out. <br>  <a href='/'> Login </a>"


@app.route('/users/<username>')
def user_by_name(username):
    users = get_users(); 
    if is_admin(users):
        if username in column(users, 1):
            user = users[column(users, 1).index(username)]
            return render_template('user.html', user = user)
        else:
            return "There is no such user. <br>" + users()
    else:
        return "You don't have a permission to view users. <br>" + books()


@app.route('/users/<int:get_id>')
def user_by_id(get_id):
    users = get_users(); 
    if is_admin(users):
        if get_id in column(users, 0):
            user = users[column(users, 0).index(get_id)]
            return render_template('user.html', user = user)
        else:
            return "There is no such user. <br>" + users()
    else:
        return "You don't have a permission to view users. <br>" + books()


app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
sess.init_app(app)
app.config.from_object(__name__)
app.debug = True
app.run()