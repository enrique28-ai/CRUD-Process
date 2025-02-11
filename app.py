from flask import Flask
from routes.process import process
from routes.auth import auth
from utils.db import db, bcrypt, login_manager
from config import DATABASE_CONNECTION_URI
import os
import secrets
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
app.register_blueprint(process)
app.register_blueprint(auth)
