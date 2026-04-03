import os
from dotenv import load_dotenv
from .base import *

load_dotenv()

DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
BASE_URL = os.environ.get('BASE_URL')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB'),
        'USER': os.environ.get('USER'),
        'PASSWORD': os.environ.get('PASS'),
        'HOST': os.environ.get('HOST'),
        'PORT': os.environ.get('PORT', '5432'),
    }
}
