'''A simple Flask server that implements a user authentication system.'''
import configparser
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

# 加载配置文件
config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.config['SECRET_KEY'] = config['DEFAULT']['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = config['DEFAULT']['DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    """A class representing a user in the system."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(512))

    def __repr__(self):
        return f'<User {self.username}>'

@app.route('/signup', methods=['POST'])
def signup():
    '''Sign up a new user.'''
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return jsonify({"error": "Invalid Input"}), 400

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"error": "Username already exists"}), 400

    user = User(username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully', 'username': user.username}), 201


@app.route('/login', methods=['POST'])
def login():
    '''Log in an existing user.'''
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return jsonify({"error": "Invalid Input"}), 400

    user = User.query.filter_by(username=username).first()

    if user is None or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid username or password"}), 400

    secret = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = secret.dumps({'id': user.id})

    max_age = int(config['DEFAULT']['COOKIE_EXPIRATION'])
    response = make_response(jsonify({'message': 'Logged in successfully'}), 200)
    response.set_cookie('token', token, max_age=max_age)

    return response

@app.route('/logout', methods=['POST'])
def logout():
    '''Log out an existing user.'''
    response = make_response(jsonify({'message': 'Logged out successfully'}), 200)
    response.set_cookie('token', '', expires=0)

    return response

@app.route('/validate', methods=['GET'])
def validate_cookie():
    '''Validate a cookie.'''
    secret = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token_cookie = request.cookies.get('token')

    if token_cookie is None:
        return jsonify({'error': 'No token cookie provided'}), 400

    try:
        data = secret.loads(token_cookie, max_age=600)
    except (BadSignature, SignatureExpired):
        return jsonify({'error': 'Invalid or expired token'}), 400

    user = db.session.get(User, data['id'])

    if user is None:
        return jsonify({'error': 'Invalid token'}), 400

    return jsonify({'message': 'Valid token', 'username': user.username})


@app.route('/v1/api/route/to/userinfo', methods=['GET'])
def get_userinfo():
    '''Get user info.'''
    token_cookie = request.cookies.get('token')
    if token_cookie is None:
        return jsonify({'message': 'No token cookie provided'}), 403

    secret = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        data = secret.loads(token_cookie)
    except BadSignature:
        return jsonify({'message': 'Invalid token'}), 403

    user = User.query.get(data['id'])
    if user is None:
        return jsonify({'message': 'Invalid token'}), 403

    return jsonify({'username': user.username}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000)
