# server/app.py

from flask import Flask, session, jsonify, request
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI='sqlite:///app.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY='super-secret-key',  # Required for session encryption
    SESSION_COOKIE_SAMESITE='None',  # Allows cross-origin cookies
    SESSION_COOKIE_SECURE=True,     # Requires HTTPS in production
)

# Configure CORS
CORS(app, 
    resources={r"/*": {"origins": "http://localhost:3000"}},
    supports_credentials=True
)

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username')).first()
        
        if not user:
            return {'error': 'Invalid username'}, 401
            
        session['user_id'] = user.id
        return user.to_dict(), 200

class Logout(Resource):
    def delete(self):
        if 'user_id' in session:
            session.pop('user_id')
        return '', 204


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            return user.to_dict(), 200
        return {'error': 'Unauthorized'}, 401

api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)