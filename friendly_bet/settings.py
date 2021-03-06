import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# valuable information read
NO_GIT_FOLDER = os.path.join(BASE_DIR, '#no_git_upload')
KEY_FILE = os.path.join(NO_GIT_FOLDER, 'key_no_git_upload.txt')
RECAPTCHA_SECRET_FILE = os.path.join(NO_GIT_FOLDER, 'recaptcha_secret_key.txt')
email_password_file = os.path.join(NO_GIT_FOLDER, 'еmail_password.txt')
with open(KEY_FILE) as f:
    SECRET_KEY = f.read().strip()

with open(RECAPTCHA_SECRET_FILE) as f:
    RECAPTCHA_SECRET = f.read().strip()

with open(email_password_file, 'r') as file:
    MAIL_PASSWORD = file.read()
    file.close()

# Developing settings - activate this set for developing

# DEBUG = True

# Deployment settings - activate this in production

DEBUG = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

ALLOWED_HOSTS = ['www.friendly-bet.club', '127.0.0.1', '192.168.0.102']

# EMAIL CONFIGURATIONS
EMAIL_HOST = 'mail.privateemail.com'
EMAIL_HOST_USER = 'no-reply@selapt.com'
EMAIL_HOST_PASSWORD = MAIL_PASSWORD
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

ADMINS = [('default', 'support@selapt.com'), ]
SERVER_EMAIL = 'no-reply@selapt.com'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'friendly_bet.urls'

TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR, ],
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

WSGI_APPLICATION = 'friendly_bet.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'captcha',
    'extra_views',
    'accounts',
    'main_app',
    'events',
    'matches',
    'predictions',
    'bonus_points',

    # 'debug_toolbar',
]

# Internationalization

LANGUAGE_CODE = 'bg-bg'

TIME_ZONE = 'Europe/Sofia'

USE_I18N = True

USE_L10N = True

USE_TZ = False

DATETIME_FORMAT = 'l, d-M-Y  @ H:i'

# Static files (CSS, JavaScript, Images)

STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    STATIC_DIR,
]
DJANGO_STATIC_FILES = os.path.join(STATIC_DIR, "#django_static_collect")
STATIC_ROOT = DJANGO_STATIC_FILES

RECAPTCHA_PRIVATE_KEY = RECAPTCHA_SECRET
RECAPTCHA_PUBLIC_KEY = '6LeY--EaAAAAACehv-84uYzCiMOmPqiOWyABaPF4'

# DEBUG TOOLBAR
# INTERNAL_IPS = ('127.0.0.1',)
