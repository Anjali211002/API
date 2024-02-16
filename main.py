from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/Api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(15), nullable=False)
    clients = db.relationship('Client', back_populates='user')


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    clients = db.relationship('Client', backref='company', lazy=True)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey(
        'company.id'), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)


class ClientUser(db.Model):
    __tablename__ = 'client_users'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey(
        'clients.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP)
    deleted_at = db.Column(db.TIMESTAMP)
    active = db.Column(db.Boolean, default=True)
    client = db.relationship('Client', back_populates='client_users')
    user = db.relationship('User', back_populates='client_users')


class CompanyUser(db.Model):
    __tablename__ = 'company_users'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey(
        'companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP)
    deleted_at = db.Column(db.TIMESTAMP)
    active = db.Column(db.Boolean, default=True)
    company = db.relationship('Company', back_populates='company_users')
    user = db.relationship('User', back_populates='company_users')


# Root route
@app.route('/')
def home():
    return "Welcome to the API!"

# List app Users


@app.route('/users', methods=['GET'])
def list_users():
    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username,
                  "email": user.email, "phone": user.phone} for user in users]
    return jsonify(user_list)

# Replace some User fields at once


@app.route('/users/<int:user_id>', methods=['PUT'])
def replace_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)

    db.session.commit()
    return jsonify({"message": "User fields replaced successfully"})

# Create some Client


@app.route('/clients', methods=['POST'])
def create_client():
    data = request.json
    user_id = data.get('user_id')
    company_id = data.get('company_id')

    if not User.query.get(user_id):
        return jsonify({"error": f"User with ID {user_id} not found"}), 404

    if not Company.query.get(company_id):
        return jsonify({"error": f"Company with ID {company_id} not found"}), 404

    new_client = Client(name=data['name'], user_id=user_id,
                        company_id=company_id, email=data['email'], phone=data['phone'])
    db.session.add(new_client)
    db.session.commit()

    return jsonify({"message": "Client created successfully"})

# Change any Client field


@app.route('/clients/<int:client_id>', methods=['PATCH'])
def change_client_field(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    data = request.json
    client.name = data.get('name', client.name)
    client.email = data.get('email', client.email)
    client.phone = data.get('phone', client.phone)

    db.session.commit()
    return jsonify({"message": "Client field(s) changed successfully"})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
