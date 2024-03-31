from django.test import TestCase
from faker import Faker

from accounts.model_factories import UserFactory
from accounts.models import LastUserMatchInputStart

fake = Faker()


class TestUser(TestCase):
    def test_get_user_names(self):
        user = UserFactory()
        self.assertEqual(f"{user.first_name} {user.last_name}", user.get_user_names())

        user.first_name = ""
        user.save()
        self.assertEqual(user.last_name, user.get_user_names())

        user.last_name = ""
        first_name = fake.first_name()
        user.first_name = first_name
        user.save()
        self.assertEqual(user.first_name, user.get_user_names())

        user.first_name = ""
        user.last_name = ""
        user.save()
        self.assertEqual(user.username, user.get_user_names())

    def test_str(self):
        user = UserFactory()
        self.assertEqual(user.username, str(user))


class TestLastUserMatchInputStart(TestCase):
    def test_str(self):
        user = UserFactory()
        obj = LastUserMatchInputStart.objects.create(user=user)
        self.assertEqual(user.username, str(obj))

    def test_started_on(self):
        user = UserFactory()
        obj = LastUserMatchInputStart.objects.create(user=user)
        initial = obj.started_on
        obj.save()
        self.assertNotEqual(initial, obj.started_on)
