from flask import render_template,request,url_for,flash,redirect,session
from app import app
from extension import db
from datetime import datetime, time
from models import db, Admin,User,Subject,Quiz,Question,Chapter,Scores
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import Config
from sqlalchemy import func

ADMIN_USERNAME = Config.ADMIN_USERNAME
ADMIN_PASSWORD = Config.ADMIN_PASSWORD

@app.route('/')
def index():
     db.create_all()
     if not Admin.query.first():
         new_admin= Admin(username ="admin", password="adminpassword@123")
         db.session.add(new_admin)
         db.session.commit()
         return render_template('index.html')
     else:    
      return render_template('index.html')

   
# --------------------------------------------------------------------login----------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
      username=request.form.get('username')
      password=request.form.get('password')

      if not username or not password:
        flash("Enter username and password")
        return redirect(url_for('login'))
      
      admin=Admin.query.filter_by(username=username).first()

      if admin and admin.password == password:
          flash("Admin logged in successfully")
          session['user_id'] = admin.id
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
    return render_template('login.html')

# ----------------------------------------------------------------login end-------------------------------------------------------------------------

#-----------------------------------------------------------------register--------------------------------------------------------------------------     
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':

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
      flash("Registration successfull", "success")
      return redirect(url_for('login'))
    
    return render_template('register.html')
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
    flash("Updated successfully")
    return redirect(url_for('user_dashboard'))


# -------------------------------------------------------------------logout-----------------------------------------------------------------------------------
@app.route('/logout')
def logout():
    session.pop('user_id')
    flash("Log out successfully!!")
    return redirect(url_for('login'))

# ----------------------------------------------------------------Admin Dashboard-----------------------------------------------------------------------
@app.route('/admin')

def admin():
    query = request.args.get("query","").strip().lower()
    print(f"Search Query: '{query}'")
    query = query.strip()
    if query:
        subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    else:    
        subjects = Subject.query.all()
    print(f"Matching Subjects: {subjects}")    
    if not subjects:
        print("No subjects matched the query.")
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
    # quiz = Quiz.query.first()       
    
    return render_template('admin.html',subjects=subjects,sub_chapters=sub_chapters, chapter_quizs= chapter_quizs, question_counts = chapter_question, query=query)

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
            Quiz.query.filter_by(chapter_id=chapter.id).delete()
            db.session.delete(chapter)
        db.session.delete(subject) 
        db.session.commit()
        return redirect(url_for('admin'))  
    else:
        return "Subject not found", 404

# ----------------------------------------------------------------edit subject-------------------------------------------------------------------
@app.route('/subject/edit/<int:subject_id>', methods=['GET','POST'])
def edit_sub(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        subject_name = request.form.get("subject_name")
        subject_description= request.form.get("subject_description")

        if subject_name:
          subject.name = subject_name

        if subject_description:
          subject.description = subject_description  

        db.session.commit()    
        flash("Subject updated successfully", "success")
        return redirect(url_for('admin'))

    return render_template("edit_subject.html", subject= subject)

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
    query = request.args.get("query", "").strip().lower()
    chapters = Chapter.query.all()
    if query:
        filtered_chap = Chapter.query.filter(Chapter.name.like(f"%{query}%")).all()
        chapter_ids = [chapter.id for chapter in filtered_chap]
        quizzes = Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids)).all()
    else:    
        quizzes=Quiz.query.all()
    
    return render_template('quiz_management.html', quizzes=quizzes, chapters=chapters, query=query)
    
#------------------------------------------------------------new quiz ------------------------------------------------------------------
@app.route('/quiz/new', methods=['GET','POST'])
def new_quiz():
    if request.method == 'POST':
        chapter_id=request.form.get('chapter_id')
        date_of_quiz1 = request.form.get('date_of_quiz')
        if not date_of_quiz1:
            date_of_quiz=datetime.today().date()
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
    
# ---------------------------------------------------------------------------------update quiz-------------------------------------------------------------------------------
@app.route('/quiz/update/<int:quiz_id>', methods=['GET','POST'])
def edit_quiz(quiz_id):
    quiz= Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        print(f"Updating Quiz ID: {quiz.id}")

        quiz.chapter_id = request.form.get('chapter_id')
        date_of_quiz_str = request.form.get('date_of_quiz')
        if date_of_quiz_str:
            quiz.date_of_quiz= datetime.strptime(date_of_quiz_str, "%Y-%m-%d").date()
        else:
            quiz.date_of_quiz = datetime.today().date()  

        quiz.time_duration = request.form.get('time_duration')    
        quiz.notes = request.form.get('notes')
        try:
           db.session.commit()
           flash("Quiz updated successfullly", "success")
        except Exception as e:
           db.session.rollback()    
           flash("error")
        return redirect( url_for('quizz') )

    else:
        chapters=Chapter.query.all()
        return render_template('edit_quiz.html', quiz=quiz, chapters=chapters)

    


        
   
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
    

# ---------------------------------------------------------------------------------quiz details---------------------------------------------------------------------------------------
@app.route('/quiz/details/<int:quiz_id>', methods=['GET'])
def quiz_details(quiz_id):
    quiz= Quiz.query.get_or_404(quiz_id)
    if quiz:
        chapter= Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        quiz_details ={
            'quiz_id': quiz.id,
            'chapter_name':chapter.name,
            'chapter_description':chapter.description,
            'subject_name':subject.name,
            'subject_description':subject.description,
            'date_of_quiz': quiz.date_of_quiz,
            'time_duration':quiz.time_duration,
            'no_of_questions': quiz.no_of_questions,
            'notes':quiz.notes
        }
        return render_template('quiz_details.html', quiz_details=quiz_details)
    else:
        flash ("Quiz not found", 404)
        return redirect(url_for('quizz'))


# ----------------------------------------------------------------------------------Add Questions-------------------------------------------------------------------------------------   
@app.route('/question/add/<int:quiz_id>', methods=['GET','POST'])
def add_questions(quiz_id):
        quiz =Quiz.query.get(quiz_id)
        if not quiz:
            return "Quiz not found", 404
        

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
              
        return render_template('add_question.html',quiz=quiz) 
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
# ----------------------------------------------------------------------------------edit questions------------------------------------------------------------------------
@app.route('/question/edit/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question= Question.query.get_or_404(question_id)
    print(question.__dict__)
    if request.method == 'POST':
        question.question_title = request.form.get('question_title')
        question.question_text = request.form.get('question_text')
        question.option1 = request.form.get('option1')
        question.option2 = request.form.get('option2')
        question.option3 = request.form.get('option3')
        question.option4 = request.form.get('option4')
        question.correct_option = int(request.form.get('correct_option'))
        db.session.commit()
        flash('Question updated successfully')
        return redirect(url_for('quizz'))
    return render_template('edit_question.html', question=question)



# --------------------------------------------------------------------------------user dashboard----------------------------------------------------------------------------------------
@app.route('/user_dashboard', methods=['GET','POST'])
def user_dashboard():
    query = request.args.get("query", "").strip().lower()
    search_type = request.args.get("search_type", "select")
    quizzes= Quiz.query.all()
    quiz_data = []

    if query:
        if search_type == "subject":    
           matched_subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
           subject_ids = [subject.id for subject in matched_subjects]
           matched_chapters =Chapter.query.filter(Chapter.subject_id.in_(subject_ids)).all()
           chapter_ids = [chapter.id for chapter in matched_chapters]
           quizzes= Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids)).all()
        elif search_type == "chapter":
            matched_chapters = Chapter.query.filter(Chapter.name.ilike(f"%{query}%")).all()
            chapter_ids = [chapter.id for chapter in matched_chapters]
            quizzes = Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids)).all()

        elif search_type == "date":
            search_date = datetime.strptime(query, "%Y-%m-%d").date()
            quizzes = Quiz.query.filter(Quiz.date_of_quiz == search_date).all()
        
    for quiz in quizzes:
        chapter= Chapter.query.get(quiz.chapter_id)
        question_count = Question.query.filter_by(quiz_id=quiz.id).count()
        quiz_data.append((quiz,chapter, question_count))
    return render_template('user_dashboard.html', quizzes=quiz_data,query = query, search_type= search_type)
        


# -------------------------------------------------------dispaly and attempt quiz --------------------------------------------------------------------------------------
@app.route('/user/quiz_attempt/<int:quiz_id>/<int:question_num>', methods=['GET','POST'])
def quiz_attempt(quiz_id, question_num):
     user_id = session.get('user_id',1)
     if not user_id:
         flash("First logged in to attempt the quiz")
         return redirect(url_for('login'))
     quiz = Quiz.query.get(quiz_id)
     questions= Question.query.filter_by(quiz_id = quiz_id).all()

     if not quiz or not questions:
         flash("Quiz or questions not found", "danger")
         return redirect(url_for('user_dashboard'))
     
     quiz_duration= quiz.time_duration
     
     if question_num ==1:
         session['quiz_start_time'] = datetime.now().isoformat()

         existing_score = Scores.query.filter_by(user_id = user_id, quiz_id = quiz_id).first()
         if existing_score:
             existing_score.total_scored = 0
             existing_score.date_of_attempt= datetime.today().date()
             existing_score.time_taken = time(0,0,0)
             db.session.commit()

     total_time_seconds = 0       

     if 'quiz_start_time' in session:
         start_time = datetime.fromisoformat(session['quiz_start_time']) 
         total_time_seconds  = (datetime.now() - start_time).total_seconds() 
         hours = int(total_time_seconds // 3600)  
         minutes = int((total_time_seconds % 3600) // 60)
         seconds = int(total_time_seconds % 60)
     
     if total_time_seconds > (quiz_duration * 60):
      flash("Time is up!!", "warning")
      return redirect(url_for('user_dashboard'))
         
         

     if question_num > len(questions):
         flash("you are done!")
         return redirect(url_for('submit_quiz',quiz_id = quiz_id))
     
     question = questions[question_num - 1]

     if request.method == 'POST' :
         selected_option = request.form.get('option')
         score_entry = Scores.query.filter_by( user_id = user_id, quiz_id = quiz_id).first()
         if not score_entry:
             score_entry = Scores(
                 user_id = user_id,
                 quiz_id = quiz_id,
                 date_of_attempt = datetime.today().date(),
                 time_taken= time(0,0,0),
                 total_scored= 0

             )
             db.session.add(score_entry)

         correct = selected_option and int(selected_option) == question.correct_option
         if correct:
             score_entry.total_scored += 1

         score_entry.time_taken = time(hours,minutes,seconds)    
         db.session.commit()
         return redirect(url_for('quiz_attempt', quiz_id=quiz_id, question_num = question_num + 1))
     
     return render_template("show_quiz.html", quiz=quiz, question=question, question_num = question_num, total=len(questions))

# ----------------------------------------------------------------------------quiz submission summary-------------------------------------------------------------------

@app.route('/submit_quiz/<int:quiz_id>')
def submit_quiz(quiz_id):
    user_id = session.get('user_id',1)
    if not user_id:
        flash("log in first !!")
        return redirect(url_for('login'))
    quiz =Quiz.query.get(quiz_id)
    if not quiz:
        flash("No quiz found", "warning")
        return redirect(url_for('user_dashboard'))

    score_details = Scores.query.filter_by(user_id = user_id, quiz_id= quiz_id).first()

    if not score_details:
      flash("No attempt record found", "warning")
      return redirect(url_for('user_dashboard'))
    
    time_taken1 = str(score_details.time_taken)
    return render_template('scores.html', quiz= quiz, total_score= score_details.total_scored,time_taken=time_taken1)

# ---------------------------------------------------------------------------------scores---------------------------------------------------------------------------
@app.route('/user_scores')  
def user_scores ():
    user_id= session.get('user_id')
      
    scores = Scores.query.filter_by(user_id = user_id).all()   
    if not scores:
        flash("No score record found for this quiz")
        return "No score record found for this quiz", 403
    quiz_scores=[]
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id)
        chapter_name = chapter.name if chapter else "unknown chapter"
        no_of_questions = Question.query.filter_by(quiz_id=quiz.id).count()
        
        quiz_scores.append((quiz.id, chapter_name, no_of_questions, score.date_of_attempt, score.time_taken, score.total_scored))
        
    return render_template('user_scores.html', quiz_scores=quiz_scores)    


 # ----------------------------------------------------------------------------------user summary---------------------------------------------------------------------------
@app.route('/user/summary')
def user_summary():
    user_id = session.get('user_id')
    if not user_id:
        flash("You are not logged in.log in to continue")
        return redirect(url_for('login'))
    subjects= Subject.query.all()
    sub_names=[]
    quiz_counts =[]

    for subject in subjects:
        quiz_count = Quiz.query.join(Chapter).filter(Chapter.subject_id == subject.id).count()
        sub_names.append(subject.name)
        quiz_counts.append(quiz_count)

    quiz_attempts =Scores.query.with_entities(Scores.date_of_attempt).filter_by(user_id = user_id).all()  
    monthwise_count = {}
    for attempt in quiz_attempts:
        month = attempt.date_of_attempt.strftime('%B')
        if month in monthwise_count:
            monthwise_count[month] += 1
        else:
            monthwise_count[month] = 1  
    months = list(monthwise_count.keys())   
    quizzes= list(monthwise_count.values())       

    return render_template('user_summary.html',sub_names=sub_names, quiz_counts=quiz_counts, months= months,quizzes= quizzes)

# --------------------------------------------------------------------------------------admin summary----------------------------------------------------------------------------------------
@app.route('/admin/summary')
def admin_summary():
    subject_top_scores = (
        db.session.query(Subject.name, func.max(Scores.total_scored))
        .join(Chapter, Chapter.subject_id == Subject.id)
        .join(Quiz, Quiz.chapter_id == Chapter.id)
        .join(Scores, Scores.quiz_id == Quiz.id)
        .group_by(Subject.name).all()

    )

    subject_wise_attempt = (
        db.session.query(Subject.name, func.count(Scores.user_id))
        .join(Chapter, Chapter.subject_id == Subject.id)
        .join(Quiz, Quiz.chapter_id == Chapter.id)
        .join(Scores, Scores.quiz_id == Quiz.id)
        .group_by(Subject.name).all()

    )
    subjects = [subject[0] for subject in subject_top_scores ]
    top_scores = [subject[1] for subject in subject_top_scores]

    subject_attempts = [subject[0] for subject in subject_wise_attempt]
    total_user_attempt = [subject[1] for subject in subject_wise_attempt]
    
    return render_template('admin_summary.html',subjects= subjects,top_scores=top_scores,subject_attempts = subject_attempts,total_user_attempt= total_user_attempt)
   
