from flask import Blueprint, jsonify, request
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/signup', methods=["POST"])
def signup():
    data = request.json

    if data.get('username') and data.get('email') and data.get('password'):
        queryUsername = db.select(User).where(User.username == data['username'])
        queryEmail = db.select(User).where(User.email == data['email'])
        username_exist = db.session.execute(queryUsername).scalar()
        email_exist = db.session.execute(queryEmail).scalar()

        if username_exist:
            return jsonify({'message': 'Error. Username already exists'}), 400

        if email_exist:
            return jsonify({'message': 'Error. Email already exists'}), 400
       
        hashed_password = generate_password_hash(data['password'])
        user = User(username=data['username'], email=data['email'], password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    return jsonify({'message': 'Invalid data'}), 400


@auth_bp.route('/api/login', methods=["POST"])
def login():
    data = request.json

    if data.get('email') and data.get('password'):
        query = db.select(User).where(User.email == data['email'])
        user = db.session.execute(query).scalar()

        if user and check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=str(user.id))
            return jsonify({
                'message': 'Login successful!',
                'token': access_token
            }), 200
        return jsonify({'message': 'Invalid credentials'}), 401
    return jsonify({'message': 'Email and Password are required'}), 400