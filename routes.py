from flask import render_template,request,url_for,flash,redirect,session
from app import app
from datetime import datetime
import datetime
from models import db, User,Subject,Quiz,Question,Chapter
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import ADMIN_USERNAME, ADMIN_PASSWORD

@app.route('/')
def index():
    return render_template('index.html')
    # if 'user_id' in session:
    #   return render_template('index.html')
    # else:
    #     flash("please login to continue")
    #     return redirect(url_for('login'))
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
        return redirect(url_for('admin'))

    user=User.query.filter_by(username=username).first()  

    if not user:
        flash("Username does not exists") 
        return redirect(url_for('login'))
    if not check_password_hash(user.passhash, password):
        flash('Incorrect password')
        return redirect(url_for('login'))
    
    
    session['user_id']=user.id
    flash(" User Successfully login")  
    return redirect('user_dashboard')

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
# ------------------------------------------------------------------auth----------------------------------------------------------------------------------
def auth_require(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        else:
            flash("please login to continue")
            return redirect(url_for('login'))
    return inner

# ------------------------------------------------------------------profile---------------------------------------------------------------------------

@app.route('/profile')
@auth_require
def profile():
    user=User.query.get(session['user_id'])
    return render_template('user_profile.html', user=user)

@app.route('/profile', methods=['POST'])
@auth_require

def profile_post():
    username = request.form.get('username')
    cpassword = request.form.get('cpassword')
    password = request.form.get('password')
    newname = request.form.get('fullname')

    if not username or not cpassword or not password:
      flash("please fill the required fields")
      return redirect(url_for('profile'))
    
    user = User.query.get(session['user_id'])
    if not check_password_hash(user.passhash, cpassword):
        flash("Incorrect password")
        return redirect(url_for('profile'))
    
    new_password=generate_password_hash(password)
    user.passhash=new_password
    user.fullName=newname
    db.session.commit()
    flash("Updated successfully ")
    return redirect(url_for('user_dashboard'))


# -------------------------------------------------------------------logout-----------------------------------------------------------------------------------
@app.route('/logout')

def logout():
    session.pop('user_id')
    return redirect(url_for('login'))

# ----------------------------------------------------------------Admin Dashboard-----------------------------------------------------------------------
@app.route('/admin')

def admin():
    subjects = Subject.query.all()
    sub_chapters = {}
    chapter_quizs={}
    chapter_question ={}
    for subject in subjects:
        chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        sub_chapters[subject.id]=chapters

        for chapter in chapters:
            quizzes = Quiz.query.filter_by(chapter_id= chapter.id).all()
            chapter_quizs[ chapter.id ] = quizzes
            total_question = sum(quiz.no_of_questions for quiz in quizzes)
            chapter_question[chapter.id] = total_question
    quiz = Quiz.query.first()       
    
    return render_template('admin.html',subjects=subjects,sub_chapters=sub_chapters, chapter_quizs= chapter_quizs, question_counts = chapter_question)

# ---------------------------------------------------adding subjects-------------------------------------------------------------------
@app.route('/subject/add',methods=['GET','POST'])

def add_sub():
    if request.method == 'POST':
        subject_name=request.form.get('subject_name')
        subject_description = request.form.get('subject_description')
        new_subject = Subject(name=subject_name,description=subject_description)
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for('admin'))
    else:
        return render_template('add_sub.html')   
#  ------------------------------------------------------------delete subject----------------------------------------------------------------------------
@app.route('/subject/delete/<int:subject_id>', methods=['GET','POST'])
def del_sub(subject_id):
    subject= Subject.query.get(subject_id)
    if subject:
        chapters =Chapter.query.filter_by(subject_id = subject_id).all()
        for chapter in chapters:
            Quiz.query.filter_by(chapter_id=chapter_id).delete()
            db.session.delete(chapter)
        db.session.delete(subject) 
        db.session.commit()
        return redirect(url_for('admin'))  
    else:
        return "Subject not found", 404


# ------------------------------------------adding chapter-----------------------------------------------------------------------------
@app.route('/chapter/add/<int:subject_id>', methods=['GET','POST']) 
def add_chapter(subject_id):
    subject= Subject.query.get(subject_id)
    if not subject:
        return "Subject not found",404
    if request.method == 'POST':
        chapter_name=request.form.get('chapter_name')
        chapter_description=request.form.get('chapter_description')
        new_chapter = Chapter(name=chapter_name,description= chapter_description,subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for('admin'))
    else:
        return render_template('add_chap.html',subject=subject)


# ----------------------------------------------------------updating chapter-----------------------------------------------------------
@app.route('/chapter/edit/<int:chapter_id>',methods=['GET','POST'])
def edit_chap(chapter_id):
    chapter=Chapter.query.get(chapter_id)
    if not chapter:
        return "chapter not found",404
    if request.method== 'POST':
        chapter.name=request.form.get('chapter_name')
        chapter.description=request.form.get('chapter_description')
        db.session.commit()
        return redirect(url_for('admin'))

    return render_template('edit_chapter.html',chapter=chapter)

# --------------------------------------------------------------delete chapter--------------------------------------------------------------------
@app.route('/chapter/delete/<int:chapter_id>',methods=['GET','POST'])
def del_chap(chapter_id):
    chapter=Chapter.query.get(chapter_id)
    if chapter:
        quiz=Quiz.query.filter_by(chapter_id = chapter_id).delete()
        # if quiz:
        #     db.session.delete(quiz)
        db.session.delete(chapter)
        db.session.commit()  
        return redirect(url_for('admin'))  
    else:
        return "chapter not found",404
 

# -------------------------------------------------------QUIZ PAGE--------------------------------------------------------------------------------------------
@app.route('/quizz',methods=['GET','POST'])
def quizz():
    chapters = Chapter.query.all()
    quizzes=Quiz.query.all()
    # quizz_in_chapter = {}
    # for chapter in  chapters:
    #     quizz_in_chapter[chapter.id] = Quiz.query.filter_by(chapter_id = chapter.id).all()
    #     return render_template("quiz_management.html", chapters = chapters, quizz_in_chapter = quizz_in_chapter)
    return render_template('quiz_management.html', quizzes=quizzes, chapters=chapters)
    
#------------------------------------------------------------new quiz ------------------------------------------------------------------
@app.route('/quiz/new', methods=['GET','POST'])
def new_quiz():
    if request.method == 'POST':
        chapter_id=request.form.get('chapter_id')
        date_of_quiz1 = request.form.get('date_of_quiz')
        if not date_of_quiz1:
            date_of_quiz=datetime.date.today()
        else:
            date_of_quiz=datetime.date.formisoformat(date_of_quiz1)    
        time_duration = request.form.get('time_duration')
        # no_of_questions = request.form.get('no_of_questions')
        notes = request.form.get('notes')

        new_quiz =Quiz(chapter_id=chapter_id, date_of_quiz=date_of_quiz, time_duration=time_duration, no_of_questions=0, notes=notes)
        db.session.add(new_quiz)
        db.session.commit()
        question_count =Question.query.filter_by(quiz_id = new_quiz.id).count()
        new_quiz.no_of_questions= question_count
        db.session.commit()
        return redirect(url_for('quizz'))
    else:
       chapters =Chapter.query.all()
       return render_template('new_quiz.html',chapters=chapters)
   
# --------------------------------------------------------------------------delete quiz-------------------------------------------------------------------------------------

@app.route('/quiz/delete/<int:quiz_id>', methods=['GET','POST'])
def del_quiz(quiz_id):
    quiz =Quiz.query.get(quiz_id)
    if quiz:
        Question.query.filter_by(quiz_id= quiz_id).delete()
        db.session.delete(quiz)
        db.session.commit()
        return redirect(url_for('quizz'))
    else:
        return "Quiz not found", 404


# ------------------------------------------------------------------Add Questions-------------------------------------------------------------   
@app.route('/question/add/<int:quiz_id>', methods=['GET','POST'])
def add_questions(quiz_id):
        quiz =Quiz.query.get(quiz_id)
        if not quiz:
            return "Quiz not found", 404
        
        # session['question_count'] == Question.query.filter_by(quiz_id = quiz_id).count()
        # if 'question_count' not in session or session['question_count'] >= quiz.no_of_questions:
        #     session['question_count'] = 0
            # session[ 'question_count' ] = Question.query.filter_by(quiz_id = quiz_id).count()

        if request.method == 'POST':
            question_text= request.form.get('question_text')
            question_title=  request.form.get('question_title')
            option1= request.form.get('option1')
            option2=  request.form.get('option2')
            option3= request.form.get('option3')
            option4= request.form.get('option4')
            correct_option= request.form.get('correct_option')
            new_question = Question(quiz_id=quiz_id,
                                    question_text=question_text,
                                      question_title=question_title,
                                      option1=option1,
                                      option2=option2,
                                      option3=option3,
                                      option4=option4,
                                      correct_option=correct_option)
            
            db.session.add(new_question)
            db.session.commit()
            quiz.no_of_questions +=1
            db.session.commit()
            session[ 'question_count' ] += 1
            # if session[ 'question_count' ] < quiz.no_of_questions:
            #     # session.pop('question_count', None)
            #     print('redirect to next page')
            #     return redirect(url_for('add_questions', quiz_id=quiz_id))
            # else:
            #     session.pop('question_count', None)
            #     return redirect(url_for('quizz'))       
        return render_template('add_question.html',quiz=quiz) # question_count=session[ 'question_count' ]+1
# --------------------------------------------------------------------------delete question--------------------------------------------------------------------------------
@app.route('/question/delete/<int:question_id>',methods=['GET','POST'])
def del_question(question_id):
    question= Question.query.get(question_id)
    if question :
      quiz_id = question.quiz_id
      quiz = Quiz.query.get(quiz_id)

      db.session.delete(question)
      db.session.commit()

      if quiz.no_of_questions > 0:
          quiz.no_of_questions -= 1
          db.session.commit()
      
      return redirect(url_for('quizz'))


# --------------------------------------------------------------------------------user dashboard----------------------------------------------------------------------------------------
@app.route('/user_dashboard', methods=['GET','POST'])
def user_dashboard():
    return render_template('user_dashboard.html')
        




        