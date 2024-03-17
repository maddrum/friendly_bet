from .local import *

DEBUG = True

ALLOWED_HOSTS = ["*"]
# needed for django_coverage_plugin
TEMPLATES[0]["OPTIONS"]["debug"] = True

# browser test settings
TEST_SERVER_HOST = os.getenv("TEST_SERVER_HOST", "web")
RECAPTCHA_PRIVATE_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
RECAPTCHA_PUBLIC_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
SILENCED_SYSTEM_CHECKS = ["django_recaptcha.recaptcha_test_key_error"]
TEST_ARTIFACT_FOLDER = os.path.join(BASE_DIR, "__browser_tests", "artifacts")
