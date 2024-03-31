from django.template import Context, Template
from django.test import TestCase

from matches.model_factories import MatchResultFactory
from matches.models import Match
from matches.tools import create_match_result, initialize_matches


class TestTemplateTags(TestCase):
    def setUp(self):
        super().setUp()
        initialize_matches()

    def test_get_match_home_result(self):
        match_result = create_match_result(match=Match.objects.first())
        match_result.match_is_over = False
        match_result.score_home = 2
        match_result.score_after_penalties_home = 3
        match_result.save()

        template = Template("{% load matches_tags %} {% get_match_home_result obj %}")
        rendered = template.render(Context({"obj": match_result}))
        self.assertEqual(str(None), str(rendered).strip())

        match_result.match_is_over = True
        match_result.penalties = False
        match_result.save()

        template = Template("{% load matches_tags %} {% get_match_home_result obj %}")
        rendered = template.render(Context({"obj": match_result}))
        self.assertEqual(str(2), str(rendered).strip())

        match_result.penalties = True
        match_result.save()

        template = Template("{% load matches_tags %} {% get_match_home_result obj %}")
        rendered = template.render(Context({"obj": match_result}))
        self.assertEqual(str(3), str(rendered).strip())

    def test_get_match_guest_result(self):
        match_result = create_match_result(match=Match.objects.first())
        match_result.match_is_over = False
        match_result.score_guest = 6
        match_result.score_after_penalties_guest = 7
        match_result.save()

        template = Template("{% load matches_tags %} {% get_match_guest_result obj %}")
        rendered = template.render(Context({"obj": match_result}))
        self.assertEqual(str(None), str(rendered).strip())

        match_result.match_is_over = True
        match_result.penalties = False
        match_result.save()

        template = Template("{% load matches_tags %} {% get_match_guest_result obj %}")
        rendered = template.render(Context({"obj": match_result}))
        self.assertEqual(str(6), str(rendered).strip())

        match_result.penalties = True
        match_result.save()

        template = Template("{% load matches_tags %} {% get_match_guest_result obj %}")
        rendered = template.render(Context({"obj": match_result}))
        self.assertEqual(str(7), str(rendered).strip())
