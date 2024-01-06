from django.forms import BaseModelFormSet


class PredictionFormSet(BaseModelFormSet):
    def __init__(self, matches, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.matches = matches

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        try:
            kwargs["home_team"] = self.matches[index].home.name
            kwargs["guest_team"] = self.matches[index].guest.name
            kwargs["phase"] = self.matches[index].phase
        except IndexError:
            pass
        return kwargs
