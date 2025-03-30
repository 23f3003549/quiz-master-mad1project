
from extension import db

class Admin(db.Model):
    id= db.Column(db.Integer, primary_key =True, autoincrement=True)
    username = db.Column(db.String(35), unique=True, nullable=False)
    password = db.Column(db.String(30), unique = True, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(35), unique=True, nullable=False)
    passhash=db.Column(db.String(256), nullable=False)
    fullName=db.Column(db.String(70), nullable=False)
    qualification=db.Column(db.String(50))
    dob=db.Column(db.Date, nullable=True)
    score=db.relationship('Scores', backref='user', lazy=True)

class Subject(db.Model):
    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    name= db.Column(db.String(50), nullable=False)
    description=db.Column(db.String(200), nullable=True)
    chapters=db.relationship('Chapter', backref='subject', lazy=True)

class Chapter(db.Model):
    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id=db.Column(db.Integer, db.ForeignKey('subject.id', name='FK_chapter_subject_id'), nullable=False)
    name=db.Column(db.String(50), nullable=False)
    description=db.Column(db.String(100), nullable=True)
    quizs=db.relationship('Quiz', backref='chapter', lazy=True)
    

class Quiz(db.Model):
    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id=db.Column(db.Integer, db.ForeignKey('chapter.id', name='FK_quiz_chapter_id'), nullable=False)
    date_of_quiz=db.Column(db.Date, nullable=False)
    time_duration= db.Column(db.Integer, nullable=False)
    no_of_questions=db.Column(db.Integer, nullable=True)
    notes=db.Column(db.String(50), nullable=True)
    questions=db.relationship('Question', backref='quiz', lazy=True)
    score=db.relationship('Scores', backref='quiz', lazy=True)
    

class Question(db.Model):
    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id=db.Column(db.Integer, db.ForeignKey('quiz.id', name='FK_question_quiz_id'), nullable=False) 
    question_title=db.Column(db.String(200), nullable=False) 
    question_text=db.Column(db.String(200), nullable=False)
    option1=db.Column(db.String(100), nullable=False)
    option2=db.Column(db.String(100), nullable=False) 
    option3=db.Column(db.String(100), nullable=False) 
    option4=db.Column(db.String(100), nullable=False) 
    correct_option=db.Column(db.Integer, nullable=False) 

class Scores(db.Model):
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer,db.ForeignKey('quiz.id', name='FK_scores_quiz_id'), nullable=False)
    user_id= db.Column(db.Integer,db.ForeignKey('user.id', name='FK_scores_user_id'), nullable=False)
    date_of_attempt= db.Column(db.Date, nullable=False)
    time_taken= db.Column(db.Time, nullable=False)
    total_scored= db.Column(db.Integer, nullable=False)


     
           