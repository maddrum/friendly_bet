from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import path, reverse_lazy

from accounts import views

urlpatterns = [
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path(
        "register-success/",
        views.UserRegisterSuccessView.as_view(),
        name="register_success",
    ),
    path("login/", LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="../thank-you"), name="logout"),
    path("thank-you/", views.ThankYouView.as_view(), name="thank_you"),
    path("profile/", views.UserPredictionsListView.as_view(), name="profile"),
    path(
        "profile-history-and-points/",
        views.ProfilePredictionStats.as_view(),
        name="profile_history",
    ),
    path(
        "profile-settings/",
        views.UserSettingsUpdateView.as_view(),
        name="profile_settings",
    ),
    path(
        "password-change/",
        PasswordChangeView.as_view(
            template_name="accounts/password-change.html",
            success_url=reverse_lazy("login"),
        ),
        name="password_change",
    ),
    path("logout-confirm/", views.ProfileLogoutConfirm.as_view(), name="logout_confirm"),
]
