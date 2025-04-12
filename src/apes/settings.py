"""
Django settings for apes project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

import environ

env = environ.Env()

environ.Env.read_env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "*",
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # User Apps
    'pages',
    'session',
    'courses',
    'preferences',

    #'storages',
    #'corsheaders',
]

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# for login authentication; default authentication backend
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', 
]

# URL for login, internal user pages are redirected to this if user is not logged in
# used via @login_required decorator in restricted user views (e.g., homepage_view, etc.)
LOGIN_URL = "/login/"

# user cookies reset
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# SESSION_COOKIE_AGE = <someValue>
"""if we want user cookies to be saved definitely (time-bound), just set SESSION_COOKIE_AGE to some value in seconds
however, as SESSION_COOKIE_AGE is not set to any value, this means that Django keeps the actively tracks the session
UNTIL the browser is ultimately closed (as in-the entire browser (all tabs!)); closing the entire browser -> terminates session
"""


# AUTHENTICATION_BACKENDS = [
#     "django.contrib.auth.backends.ModelBackend",  # Default authentication
# ]

ROOT_URLCONF = 'apes.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'apes.wsgi.application'

MIDDLEWARE = [
    'apes.middleware.DatabaseErrorMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

""" CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOWED_ORIGINS = [
    "https://cs192-apes.onrender.com",
    "http://127.0.0.1"
] """

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

""" DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3', 
    }
} """

# Render PostgreSQL database

import dj_database_url

DATABASES = {
    'default' : dj_database_url.parse(env('DATABASE_URL'))
}


# orig: BASE_DIR / 'db.sqlite3'

# tester: 'test_db.sqlite3'
# NOTE: can have any name ^ since merely a tester (don't migrate since migrating creates a new database/table which would hence allow database operations)

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = "session.Student"


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_DIR = os.path.join (BASE_DIR, "static")
STATIC_ROOT = os.path.join (BASE_DIR,'static files')

STATIC_URL ='/static/'# path to read css with local (probably)
STATICFILES_DIRS = [
        os.path.join (BASE_DIR, "static"),
    ]
# https://stackoverflow.com/questions/71873839/how-to-make-static-directory-in-django (enes islam)

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AWS configuration
""" 
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')

# Basic storage config for Amazon S3

AWS_STORAGE_BUCKET_NAME = 'apes-192'

AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

AWS_S3_FILE_OVERWRITE = False

STORAGES = {

    # Media file (image) management   
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
    },
    
    # CSS and JS file management
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
    },
} """

