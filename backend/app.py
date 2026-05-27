from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

from config.db import db

from router.userroute import user_bp
from router.taskroute import task_bp

load_dotenv()

app = Flask(__name__)

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# JWT SECRET
app.config['JWT_SECRET_KEY'] = 'super-secret-key'

# SQLAlchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# INIT DB
db.init_app(app)

# INIT JWT
jwt = JWTManager(app)

# ROUTES
app.register_blueprint(
    user_bp,
    url_prefix='/api/auth'
)

app.register_blueprint(
    task_bp,
    url_prefix='/api'
)

@app.route('/')
def home():
    return "Welcome to Digital Event Networking and Interaction Platform!"

# CREATE DATABASE
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)