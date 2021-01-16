import os
from os.path import join, dirname

from dotenv import load_dotenv

# env vars
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# SQLALCHEMY
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL') or "postgresql:///higa"
SQLALCHEMY_TRACK_MODIFICATIONS = True

# OTHERS
JSON_AS_ASCII = False
SECRET_KEY = os.environ.get("SECRET_KEY")
JWT_ACCESS_TOKEN_EXPIRES = False
