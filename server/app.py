#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        campers_dict_list = [c.to_dict(rules=('-signups',)) for c in Camper.query.all()]
        return make_response(campers_dict_list, 200)
    
    def post(self):
        name = request.json.get('name')
        age = request.json.get('age')
        if not name or not age:
            return make_response({"errors": ["validation errors"]}, 400)
        if not (8 <= int(age) <= 18):
            return make_response({"errors": ["validation errors"]}, 400)

        new_camper = Camper(name=name, age=age)
        db.session.add(new_camper)
        db.session.commit()

        new_camper_data = db.session.get(Camper, new_camper.id)
        return make_response(new_camper_data.to_dict(), 201)
        
api.add_resource(Campers, '/campers')

class CamperByID(Resource):
    def get(self, id):
        if camper := Camper.query.filter(Camper.id == id).first():
            return make_response(camper.to_dict(), 200)
        return make_response({"error": "Camper not found"}, 404)
    
    def patch(self, id):
        if camper := Camper.query.filter(Camper.id == id).first():
            if not request.json.get('name') or not request.json.get('age'):
                return make_response({"errors": ["validation errors"]}, 400)
            if not (8 <= request.json.get('age') <= 18):
                return make_response({"errors": ["validation errors"]}, 400)
            for attr in request.json:
                setattr(camper, attr, request.json.get(attr))
            db.session.add(camper)
            db.session.commit()
            return make_response(camper.to_dict(rules=("-signups",)), 202)
        return make_response({"error": "Camper not found"}, 404)

api.add_resource(CamperByID, '/campers/<int:id>')

class Activities(Resource):
    def get(self):
        activites_dict_list = [a.to_dict(rules=('-signups',)) for a in Activity.query.all()]
        return make_response(activites_dict_list, 200)

api.add_resource(Activities, '/activities')

class ActivitiesByID(Resource):
    def delete(self, id):
        if activity := Activity.query.filter(Activity.id == id).first():
            db.session.delete(activity)
            db.session.commit()
            return make_response({}, 204)
        return make_response({"error": "Activity not found"}, 404)

api.add_resource(ActivitiesByID, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        camper_id = request.json.get("camper_id")
        activity_id = request.json.get("activity_id")
        time = request.json.get("time")
        if not camper_id or not activity_id or not time:
            return make_response({"errors": ["validation errors"]}, 400)
        if not (0 <= int(time) <= 23):
            return make_response({"errors": ["validation errors"]}, 400)
        
        new_signup = Signup(camper_id=camper_id, activity_id=activity_id, time=time)
        db.session.add(new_signup)
        db.session.commit()

        new_signup_data = db.session.get(Signup, new_signup.id)
        return make_response(new_signup_data.to_dict(), 201)
api.add_resource(Signups, '/signups')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
