import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.Factory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user_{n}")
    first_name = factory.Faker("first_name", locale="bg_BG")
    last_name = factory.Faker("last_name", locale="bg_BG")
