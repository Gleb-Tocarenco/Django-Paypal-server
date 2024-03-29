
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     
)

MANAGERS = ADMINS
PROJECT_ROOT = os.getcwd()
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'testapp.db'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

TIME_ZONE = "Europe/Istanbul"
LANGUAGE_CODE = 'en-us'
SITE_ID = 4
USE_I18N = True

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media")
MEDIA_URL = '/site_media/'
ADMIN_MEDIA_PREFIX = '/media/'
SECRET_KEY = '&0sk5zgk^kt@w3+!i@n6++f923@64o-1tik7)xp0873um2m1!q'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'testapp.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "templates")
)

PAYPAL_USER  = "seller_1261519973_biz_api1.akinon.com"
PAYPAL_PASSWORD = "1261519978"
PAYPAL_SIGNATURE = "A1.OnfcjaBVTgV6Yt.oT2VavxcyOA5FGVe-MrNf.1R1zNVAD6.MDOKZO"
PAYPAL_DEBUG = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'paypal',
    'testapp.base',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    )
