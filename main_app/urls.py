from django.urls import path

from main_app import views

urlpatterns = [
    path("contact/", views.SiteContactView.as_view(), name="contact"),
    path("instuctions-modal/", views.InstructionsView.as_view(), name="instructions"),
    path(
        "contact-success/",
        views.SiteContactSuccessView.as_view(),
        name="contacts_success",
    ),
]
