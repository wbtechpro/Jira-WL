"""
Django settings for jira project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+hg0e$ugtvrah2rkul0)uvi8=fssm_1193(sfq@mh@slkqcx%6'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DEBUG'))

ALLOWED_HOSTS = ['localhost', os.environ.get('SERVER_NAME')]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',

    'client.apps.ClientConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jira.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'jira.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'db-password',
        'HOST': 'db',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/jira-client-static/'
STATIC_ROOT = os.path.join(BASE_DIR, '..', 'webroot', 'jira-client-static')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}


sentry_sdk.init(
    dsn="https://57b1ef362ea1475e88927ce6eea18870@sentry.wbtech.pro/14",
    integrations=[DjangoIntegration()]
)


#####################################################################


USERNAME = os.environ.get('JIRA_USERNAME')
API_TOKEN = os.environ.get('JIRA_API_TOKEN')


FILENAME_PERCENTS = os.path.join(BASE_DIR, 'last-month-by-percents.json')  # Использовался в старых версиях, когда сохранялось в файл
FILENAME_DAY_WORKLOGS = os.path.join(BASE_DIR, 'last-day-worklogs.json')  # Использовался в старых версиях, когда сохранялось в файл
FILENAME_WEEK_WORKLOGS = os.path.join(BASE_DIR, 'last-week-worklogs.json')  # Использовался в старых версиях, когда сохранялось в файл

#  Bunch of id's for exclude from ToPercentConverter
TO_PERCENT_ID_FOR_EXCLUDE = (   # Использовался в старых версиях, когда сохранялось в файл
    '5e4e744c2110470c8da215dc',
    '557058:5ac2a471-aeb0-4190-a807-d082cff8db72',
    '557058:555ee601-6614-4cd0-9ecb-51538aad9ccd',
    '557058:3734ce03-2a43-4ecb-96fd-33351669413d',
)
