from utils.db import db
class Process(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_process_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Float, nullable=False, default=0)
    operators = db.Column(db.Integer, nullable=False, default=0)
    cycle_time = db.Column(db.Float, nullable=False, default=0)  # Expected cycle time
    units_produced = db.Column(db.Integer, nullable=False, default=0)  # ✅ New field
    setup_time = db.Column(db.Float, nullable=False, default=0)  # ✅ New field
    downtime = db.Column(db.Float, nullable=False, default=0) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 🔹 Link to the user who created it
    author = db.Column(db.String(30), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('table.id', ondelete="CASCADE"), nullable=False) 

     
class Table(db.Model):  # New Table Model
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    processes = db.relationship("Process", backref="table", lazy=True, cascade="all, delete-orphan")
