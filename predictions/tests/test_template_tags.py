from django.contrib.auth.models import AnonymousUser
from django.template import RequestContext, Template
from django.test import RequestFactory, TestCase

from accounts.model_factories import UserFactory
from matches.tools import initialize_matches
from predictions.model_factories import UserPredictionFactory
from predictions.tools import create_valid_prediction
from predictions.views_mixins import GetEventMatchesMixin


class TestTemplateTags(TestCase):
    def test_check_prediction_warning(self):
        template = Template("{% load prediction_tags %} {% check_prediction_warning %}")
        request = RequestFactory().get("")
        request.user = AnonymousUser()
        rendered = template.render(context=RequestContext(request))
        self.assertEqual(str(False), str(rendered).strip())

        user = UserFactory()
        request.user = user
        rendered = template.render(context=RequestContext(request))
        self.assertEqual(str(False), str(rendered).strip())

        initialize_matches()

        rendered = template.render(context=RequestContext(request))
        self.assertEqual(str(True), str(rendered).strip())

        mixin = GetEventMatchesMixin()
        for match in mixin.matches:
            prediction_data = create_valid_prediction()
            UserPredictionFactory(
                user=user,
                match=match,
                match_state=prediction_data.event_match_state,
                goals_home=prediction_data.goals_home,
                goals_guest=prediction_data.goals_guest,
            )

        rendered = template.render(context=RequestContext(request))
        self.assertEqual(str(False), str(rendered).strip())
