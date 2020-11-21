import os

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "postgresql:///higa"
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY="itsuka_base64"