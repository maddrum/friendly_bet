import os.path
import time
import traceback
from datetime import datetime
from functools import wraps

from django.conf import settings


def handle_failed_browser_test(test):
    @wraps(test)
    def decorated_test(self, *args, **kwargs):
        try:
            test(self, *args, **kwargs)
            return
        except Exception as exp:
            if hasattr(self, "before_freeze_datetime"):
                _datetime = self.before_freeze_datetime
            else:
                _datetime = datetime.now()
            folder = f'{_datetime.strftime("%Y-%m-%d-%H-%M")}__{self._testMethodName}__{self.__class__.__name__}'
            test_dir = os.path.join(settings.TEST_ARTIFACT_FOLDER, folder)
            if not os.path.isdir(test_dir):
                os.makedirs(test_dir)

            _write_test_path(self, test_dir=test_dir)
            _take_screenshot(self, test_dir=test_dir)
            _log_traceback(self, test_dir=test_dir, traceback_str=traceback.format_exc())
            _move_console_log(self, test_dir=test_dir)

            raise

    return decorated_test


def _get_test_name(self):
    test_name = "{classname}.{method}".format(classname=self.__class__.__name__, method=self._testMethodName)
    return test_name


def _write_test_path(self, test_dir):
    file_path = os.path.join(test_dir, "test_name.txt")
    test_module = f"{self.__class__.__module__}.{self.__class__.__name__}.{self._testMethodName}"
    with open(file_path, "w") as _dst:
        _dst.write(test_module)


def _take_screenshot(self, test_dir):
    test_name = _get_test_name(self)
    png = f"{test_name}.png"
    html = f"{test_name}.html"
    png_path = os.path.join(test_dir, png)
    html_path = os.path.join(test_dir, html)
    with open(html_path, "w") as _dst:
        _dst.write(self.browser.page_source)

    # resize to capture the whole page
    original_size = self.browser.get_window_size()
    width = self.browser.execute_script("return document.body.parentNode.scrollWidth") + 300
    height = self.browser.execute_script("return document.body.parentNode.scrollHeight") + 300
    self.browser.set_window_size(width, height)
    self.browser.save_screenshot(png_path)
    self.browser.set_window_size(original_size["width"], original_size["height"])


def _log_traceback(self, test_dir, traceback_str):
    test_name = _get_test_name(self)
    traceback_name = f"{test_name}.traceback"
    traceback_path = os.path.join(test_dir, traceback_name)
    with open(traceback_path, "w") as _dst:
        _dst.write(traceback_str)


def _move_console_log(self, test_dir):
    filename = f"{self.__module__}.console.log"
    absolute_path = os.path.join(settings.RUNLOG_FOLDER, filename)

    counter = 0
    while not os.path.isfile(absolute_path) and counter < 20:
        time.sleep(0.5)
        counter += 1

    if os.path.isfile(absolute_path):
        new_name = os.path.join(test_dir, "console.log")
        os.rename(absolute_path, new_name)
        return

    logger.error("Was not able to store logs to artefacts folder.")


def get_django_truncated_str(original_str: str, truncate_chars: int):
    """
    Get a truncated version of a string after usage of {{ some_str:truncatechars:<truncate_chars> }}

    @param original_str: The original string.
    @type original_str: str
    @param truncate_chars: The number of characters to truncate the string to.
    @type truncate_chars: int

    @return: The truncated string.
    @rtype: str

    """
    _original_str = str(original_str).strip()
    return _original_str if len(_original_str) <= truncate_chars else f"{_original_str[0:truncate_chars - 1]}…"
