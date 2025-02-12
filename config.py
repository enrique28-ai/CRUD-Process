from dotenv import load_dotenv
import os

load_dotenv()

user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
host = os.getenv('MYSQL_HOST')
database = os.getenv('MYSQL_DATABASE')
port = os.getenv('MYSQL_PORT')


DATABASE_CONNECTION_URI = f"mysql://{user}:{password}@{host}:{port}/{database}"
