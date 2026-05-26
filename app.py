from flask import Flask
from flask_jwt_extended import JWTManager

from config.db import db

from router.userroute import user_bp
from router.taskroute import task_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['JWT_SECRET_KEY'] = 'super-secret-key'

db.init_app(app)

jwt = JWTManager(app)

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

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)