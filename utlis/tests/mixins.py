import datetime
import typing

from django.utils.timezone import make_aware
from freezegun import freeze_time

if typing.TYPE_CHECKING:
    from django.test import TestCase

_BaseFreezeTimeT = typing.Union["TestCase", "BaseFreezeTimeMixin"]


class BaseFreezeTimeMixin:
    """
    Class: BaseFreezeTimeMixin

    The BaseFreezeTimeMixin class is a mixin that provides freezing of time during test cases.
    It utilizes the freezegun library to freeze the time at a specific datetime.
    This mixin is intended to be used with Django's TestCase class.

    Attributes:
    - freezer: An instance of the freezegun.FreezeTime context manager.
    - to_freeze_datetime: The datetime object to freeze the time at.
                          If not provided, it defaults to datetime.datetime(2023, 5, 15, 7, 0, 1)
                          -> 15.05.2023 07:00:01
    - before_freeze_datetime: The datetime object representing the current time before freezing.
                              This attribute is set during the setUpClass method.
    - today: The date object for the frozen datetime.

    Methods:
    - setUpClass():
    Overrides the setUpClass method of the parent class
    to set up the freezing of time before any test cases are executed.
    It starts the freezer context manager and sets the before_freeze_datetime and today attributes.
    - tearDownClass(): Overrides the tearDownClass method of the parent class to stop the freezer context manager.
    - tearDown(): Overrides the tearDown method of the parent class
                  to reset the freezer context manager to the original to_freeze_datetime.

    Example usage:

    class MyTestCase(BaseFreezeTimeMixin, TestCase):
        def test_something(self):
            # Test code here
    """

    # pylint: disable=invalid-name
    freezer = None
    to_freeze_datetime = None
    before_freeze_datetime = None  # for if you need the current time
    today = None

    @classmethod
    def setUpClass(cls: typing.Union[typing.Type["TestCase"], "BaseFreezeTimeMixin"]) -> None:
        super().setUpClass()
        cls.before_freeze_datetime = make_aware(datetime.datetime.now())
        # must be monday
        if cls.to_freeze_datetime is None:
            cls.to_freeze_datetime = make_aware(datetime.datetime(2023, 5, 15, 7, 0, 1))
        cls.freezer = freeze_time(cls.to_freeze_datetime)
        cls.freezer.start()
        cls.today = cls.to_freeze_datetime.date()

    @classmethod
    def tearDownClass(cls: typing.Union[typing.Type["TestCase"], "BaseFreezeTimeMixin"]):
        cls.freezer.stop()
        super().tearDownClass()

    def tearDown(self: _BaseFreezeTimeT):
        # Make sure that you are safe on test to change freeze time if needed.
        self.freezer.stop()
        self.freezer = freeze_time(self.to_freeze_datetime)
        self.freezer.start()

        super().tearDown()
