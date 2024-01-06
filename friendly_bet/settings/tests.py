# settings to run tests with
# Use
#   python manage.py test --settings=friendly_bet.settings.tests
from .base import *

BASE_DIR = BASE_DIR
DEBUG = True

ALLOWED_HOSTS = ["*"]
# needed for django_coverage_plugin
TEMPLATES[0]["OPTIONS"]["debug"] = True

RECAPTCHA_PRIVATE_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
RECAPTCHA_PUBLIC_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
SILENCED_SYSTEM_CHECKS = ["django_recaptcha.recaptcha_test_key_error"]
