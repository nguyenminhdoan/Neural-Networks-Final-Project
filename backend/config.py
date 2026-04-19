import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'comp258-neural-network-project-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI',
        f"sqlite:///{os.path.join(BASE_DIR, 'student_data.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATA_FILE = os.environ.get(
        'DATA_FILE',
        os.path.join(PROJECT_DIR, 'Student data.csv'),
    )
    MODEL_DIR = os.environ.get(
        'MODEL_DIR',
        os.path.join(BASE_DIR, 'saved_models'),
    )
