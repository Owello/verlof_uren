import os
import sys


IS_TEST = sys.argv[1] == 'test'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6gx96a$(%u8h*^5frt%*zk4bb(9z7%=-w!36f_w5sic#%tnj=g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Application definition

INSTALLED_APPS = [
    'registration.apps.RegistrationConfig',
    'authentication.apps.AuthenticationConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

]

MIDDLEWARE = [
    'csp.middleware.CSPMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CSP_CONFIGURATION = {
    'default': {
        'default-src': ["'none'"],
        'img-src': ["'self'", 'data:'],
        'font-src': ["'self'"],
        'style-src': ["'self'"],
        'script-src': ["'self'"],
        'object-src': ["'none'"],
        'media-src': ["'self'"],
        'prefetch-src': ["'self'"],
        'connect-src': ["'self'"],
        'frame-ancestors': ["'self'"],
        'base-uri': ["'self'"],
        'form-action': ["'self'"],
        'report-uri': 'https://log.owello.nl/api/11/csp-report/?sentry_key=27d84714ae7f427dab790afdf36e7fa3'
    },
    'unsafe': {
        'style-src': ["'unsafe-inline'"],
        'script-src': ["'unsafe-inline'", "'unsafe-eval'"],
    },
    'semantic': {
        'style-src': ['https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.css'],
        'script-src': ['https://code.jquery.com/jquery-3.1.1.min.js', 'https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.js'],
        'font-src': ['data:', 'https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/themes/default/assets/fonts/'],
    },
    'log': {
        'connect-src': ['log.owello.nl'],
        'img-src': ['log.owello.nl'],
    },
    'googleFonts': {
        'font-src': ['fonts.gstatic.com'],
        'style-src': ['fonts.googleapis.com'],
    },
}


def csp(items=None):
    csp_result = {}
    if items is None:
        items = CSP_CONFIGURATION.keys()
    for item in items:
        for csp_item, csp_values in CSP_CONFIGURATION[item].items():
            if isinstance(csp_values, list):
                if csp_item not in csp_result:
                    csp_result[csp_item] = []
                csp_result[csp_item] += csp_values
            else:
                csp_result[csp_item] = csp_values
    # Remove duplicate values
    for key, value in csp_result.items():
        if isinstance(value, list):
            csp_result[key] = list(set(value))
    return csp_result


if IS_TEST:
    INSTALLED_APPS.remove('debug_toolbar')
    MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'absence.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'registration.context_processors.default_entitlement',
            ],
        },
    },
]

WSGI_APPLICATION = 'absence.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'nl-nl'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

LOGIN_REDIRECT_URL = 'index'


try:
    from .settings_local import *
except ImportError as e:
    print("Importing local_settings.py causes exception: " + str(e))


CSP_TARGETS = {
    'cms': csp(['default', 'unsafe', 'semantic', 'log', 'googleFonts']),
}

CSP_DEFAULT_SRC = CSP_TARGETS['cms'].get('default-src')
CSP_SCRIPT_SRC = CSP_TARGETS['cms'].get('script-src')
CSP_IMG_SRC = CSP_TARGETS['cms'].get('img-src')
CSP_OBJECT_SRC = CSP_TARGETS['cms'].get('object-src')
CSP_MEDIA_SRC = CSP_TARGETS['cms'].get('media-src')
CSP_PREFETCH_SRC = CSP_TARGETS['cms'].get('prefetch-src')
CSP_FRAME_SRC = CSP_TARGETS['cms'].get('frame-src')
CSP_FONT_SRC = CSP_TARGETS['cms'].get('font-src')
CSP_CONNECT_SRC = CSP_TARGETS['cms'].get('connect-src')
CSP_STYLE_SRC = CSP_TARGETS['cms'].get('style-src')
CSP_BASE_URI = CSP_TARGETS['cms'].get('base-uri')
CSP_CHILD_SRC = CSP_TARGETS['cms'].get('child-src')
CSP_FRAME_ANCESTORS = CSP_TARGETS['cms'].get('frame-ancestors')
CSP_FORM_ACTION = CSP_TARGETS['cms'].get('form-action')
CSP_SANDBOX = CSP_TARGETS['cms'].get('sandbox')
CSP_REPORT_URI = CSP_TARGETS['cms'].get('report-uri')


