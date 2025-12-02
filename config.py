import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'manimjustsoamazingwiththisshititmakesmefeellikeiwanttokillmyselfpleasehelpmesomeonesaveme'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'mysql+mysqlconnector://root:password@localhost/notes_app_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
