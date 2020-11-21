import os
from os.path import join, dirname
from dotenv import load_dotenv
load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "postgresql:///higa"
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY=os.environ.get("SECRET_KEY")
SECRET_WORD=os.environ.get("SECRET_WORD")