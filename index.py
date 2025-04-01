from app import app
from utils.db import db
import os
with app.app_context():
    db.create_all()
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)