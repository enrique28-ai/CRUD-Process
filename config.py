from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_CONNECTION_URI = os.getenv("MYSQL_URL")
