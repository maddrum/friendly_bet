import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# VALUABLE INFORMATION
SECRET_KEY = os.environ.get("FRIENDLY_BET_DJANGO_SECRET_KEY")
RECAPTCHA_SECRET = os.environ.get("FRIENDLY_BET_GOOGLE_RECAPTCHA_SECRET_KEY")

# SECURITY
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "friendly_bet": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        },
    },
}

# EMAIL CONFIGURATIONS
EMAIL_HOST = os.environ.get("FRIENDLY_BET_EMAIL_HOST")
EMAIL_HOST_USER = os.environ.get("FRIENDLY_BET_EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("FRIENDLY_BET_MAIL_PASSWORD")
EMAIL_PORT = os.environ.get("FRIENDLY_BET_EMAIL_PORT", 465)
EMAIL_USE_TLS = os.environ.get("FRIENDLY_BET_EMAIL_USE_TLS", False) == "True"
EMAIL_USE_SSL = os.environ.get("FRIENDLY_BET_EMAIL_USE_SSL", True) == "True"

# EMAILS
ADMIN_EMAIL = os.environ.get("FRIENDLY_BET_ADMIN_EMAIL")
ADMINS = [
    ("default", ADMIN_EMAIL),
]
SERVER_EMAIL = os.environ.get("FRIENDLY_BET_SERVER_EMAIL")

AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = "friendly_bet.urls"

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            TEMPLATE_DIR,
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "friendly_bet.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_recaptcha",
    "extra_views",
    "accounts",
    "main_app",
    "events",
    "matches",
    "predictions",
    "ranklists"
    # 'debug_toolbar',
]

# Internationalization

LANGUAGE_CODE = "bg-bg"

TIME_ZONE = "Europe/Sofia"

USE_I18N = True

USE_L10N = True

USE_TZ = False

DATETIME_FORMAT = "l, d-M-Y  @ H:i"

version_file = open(os.path.join(BASE_DIR, "VERSION"), "r")
VERSION = version_file.read().strip()
version_file.close()

# Static files (CSS, JavaScript, Images)
STATIC_DIR = os.path.join(BASE_DIR, "static")
STATIC_URL = f"/static.{VERSION}/"
STATICFILES_DIRS = [
    STATIC_DIR,
]
DJANGO_STATIC_FILES = os.path.join(BASE_DIR, "static_collect")
STATIC_ROOT = DJANGO_STATIC_FILES

RECAPTCHA_PRIVATE_KEY = RECAPTCHA_SECRET
RECAPTCHA_PUBLIC_KEY = "6LeY--EaAAAAACehv-84uYzCiMOmPqiOWyABaPF4"

# DEBUG TOOLBAR
# INTERNAL_IPS = ('127.0.0.1',)

# ------------------APP SETTINGS------------------
PREDICTION_MINUTES_BEFORE_MATCH = 5
