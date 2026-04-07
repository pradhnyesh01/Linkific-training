import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DB_URI = os.getenv("DATABASE_URL")
JWT_SECRET_KEY = "super-secret-key"