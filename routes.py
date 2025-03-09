from flask import render_template,request,url_for,flash,redirect,session
from app import app
from datetime import datetime
from models import db, User,Subject,Quiz,Question,Chapter
from werkzeug.security import generate_password_hash, check_password_hash
from config import ADMIN_USERNAME, ADMIN_PASSWORD

@app.route('/')
def index():
    return render_template('index.html')
# --------------------------------------------------------------------login----------------------------------------------------------------------
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username=request.form.get('username')
    password=request.form.get('password')

    if not username or not password:
        flash("Enter username and password")
        return redirect(url_for('login'))
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return "welcome admin"

    user=User.query.filter_by(username=username).first()  

    if not user:
        flash("Username does not exists") 
        return redirect(url_for('login'))
    if not check_password_hash(user.passhash, password):
        flash('Incorrect password')
        return redirect(url_for('login'))
    
    
    
    return " User Successfully login"

# ----------------------------------------------------------------login end-------------------------------------------------------------------------

#-----------------------------------------------------------------register-------------------------------------------------------------------------- 
@app.route('/register')
def register():
    return render_template('register.html')

    
@app.route('/register', methods=['POST'])
def register_post():
    username=request.form.get('username')
    password=request.form.get('password')
    c_password=request.form.get('password1')
    fullname=request.form.get('fullname')
    qualification=request.form.get('qualification')
    dob=request.form.get('dob')
    date_object=datetime.strptime(dob,'%Y-%m-%d')
    
    if not username or not password or not c_password:
        flash("please fill out these fields")
        return redirect(url_for('register'))
    if password!=c_password:
        flash("Password do not match ")
        return redirect(url_for('register'))
    user = User.query.filter_by(username=username).first()
    if user:
        flash('Username is already exists')
        return redirect(url_for('register'))
    
    password_hash=generate_password_hash(password)
    new_user = User(username=username, passhash=password_hash, fullName=fullname, qualification=qualification, dob=date_object)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))
# ------------------------------------------------------------------register end-------------------------------------------------------------------------

