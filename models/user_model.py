from flask_login import UserMixin
from utils.db import db, login_manager, bcrypt
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    security_question = db.Column(db.String(100), nullable=False)  
    security_answer_hash = db.Column(db.String(100), nullable=False)
    processes = db.relationship('Process', backref='user', lazy=True)
    tables = db.relationship("Table", backref="user", lazy=True)



    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
    def set_security_answer(self, answer):
        """Hash the security answer before storing it."""
        self.security_answer_hash = bcrypt.generate_password_hash(answer).decode('utf-8')

    def check_security_answer(self, attempted_answer):
        """Check if the provided answer matches the stored one."""
        return bcrypt.check_password_hash(self.security_answer_hash, attempted_answer)

    