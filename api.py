from flask_restful import Resource, Api
from app import app
from models import db,User, Subject

api= Api(app)
class User1(Resource):
    def get(self):
        users =User.query.all()
        return {
            'users': [{
                'id':user.id,
                'name':user.username
            } for user in users]
        }

api.add_resource(User1, '/hello')

class SubjectResources(Resource):
    def get(self):
        subjects = Subject.query.all()
        return {
            'subjects':[
                {
                    'id':subject.id,
                    'name':subject.name,
                    'description':subject.description
                } for subject in subjects
            ]
        }
    
api.add_resource( SubjectResources , '/subject')