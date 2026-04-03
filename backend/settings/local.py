import os
from dotenv import load_dotenv
from .base import *

load_dotenv()

DEBUG = True
ALLOWED_HOSTS = ['*']
BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:8000')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB'),
        'USER': os.environ.get('USER'),
        'PASSWORD': os.environ.get('PASS'),
        'HOST': os.environ.get('HOST', 'localhost'),
        'PORT': os.environ.get('PORT', '5432'),
    }
}
