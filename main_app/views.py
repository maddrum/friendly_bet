from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView

from main_app.forms import ContactForm
from main_app.models import SiteContact


class Index(TemplateView):
    template_name = 'main_app/index.html'


class InstructionsView(TemplateView):
    template_name = 'main_app/match_instructions.html'


class SiteContactView(CreateView):
    model = SiteContact
    success_url = reverse_lazy('contacts_success')
    template_name = 'main_app/contacts.html'
    form_class = ContactForm


class SiteContactSuccessView(TemplateView):
    template_name = 'main_app/contacts-success.html'
