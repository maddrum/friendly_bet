import factory
from factory.fuzzy import FuzzyInteger

from accounts.model_factories import UserFactory
from matches.model_factories import MatchFactory
from predictions.models import UserPrediction


class UserPredictionFactory(factory.Factory):
    class Meta:
        model = UserPrediction

    user = factory.SubFactory(UserFactory)
    match = factory.SubFactory(MatchFactory)
    goals_home = FuzzyInteger(0, 10)
    goals_guest = FuzzyInteger(0, 10)
