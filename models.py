from flask_sqlalchemy import SQLAlchemy
from app import app
from flask_migrate import Migrate

# app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///db.sqlite3'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db=SQLAlchemy(app)
migrate= Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(35), unique=True)
    passhash=db.Column(db.String(256), nullable=False)
    fullName=db.Column(db.String(70), nullable=False)
    qualification=db.Column(db.String(50))
    dob=db.Column(db.Date, nullable=True)

class Subject(db.Model):
    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    name= db.Column(db.String(50), nullable=False)
    description=db.Column(db.String(200), nullable=True)
    chapters=db.relationship('Chapter', backref='subject', lazy=True)

class Chapter(db.Model):
    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id=db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    name=db.Column(db.String(50), nullable=False)
    description=db.Column(db.String(100), nullable=True)
    quizs=db.relationship('Quiz', backref='chapter', lazy=True)
    

class Quiz(db.Model):
    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id=db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz=db.Column(db.Date, nullable=False)
    time_duration= db.Column(db.Integer, nullable=False)
    no_of_questions=db.Column(db.Integer, nullable=True)
    notes=db.Column(db.String(50), nullable=True)
    questions=db.relationship('Question', backref='quiz', lazy=True)
    

class Question(db.Model):
    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id=db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False) 
    question_title=db.Column(db.String(200), nullable=False) 
    question_text=db.Column(db.String(200), nullable=False)
    option1=db.Column(db.String(100), nullable=False)
    option2=db.Column(db.String(100), nullable=False) 
    option3=db.Column(db.String(100), nullable=False) 
    option4=db.Column(db.String(100), nullable=False) 
    correct_option=db.Column(db.Integer, nullable=False) 

with app.app_context():
    db.create_all()
    db.session.commit()    

     
           