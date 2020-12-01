import os

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "postgresql:///higa"
SQLALCHEMY_TRACK_MODIFICATIONS = True
JSON_AS_ASCII=False