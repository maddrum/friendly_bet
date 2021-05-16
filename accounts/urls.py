from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from accounts import views

app_name = 'accounts'

urlpatterns = [
    url(r'register/$', views.UserRegisterView.as_view(), name='register'),
    url(r'register-success/$', views.UserRegisterSuccessView.as_view(), name='register_success'),
    url(r'login/$', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    url(r'logout/$', LogoutView.as_view(next_page='../thank-you'), name='logout'),
    url(r'thank-you/$', views.ThankYouView.as_view(), name='thank_you'),
    url(r'profile/$', views.UserPredictionsListView.as_view(), name='profile'),
    url(r'profile-match-update/(?P<pk>\d+)', views.UserUpdatePredictionView.as_view(), name='update_prediction'),
    url(r'profile-history-and-points/', views.ProfilePredictionStats.as_view(), name='profile_history'),
    url(r'profile-settings/$', views.UserSettingsUpdateView.as_view(), name='profile_settings'),
    url(r'settings-success/$', views.SettingsSuccess.as_view(), name='settings_success'),
    url(r'profile-password-change/$',
        PasswordChangeView.as_view(template_name='accounts/password-change.html', success_url='../login'),
        name='password_change'),
    url(r'bonuses/$', views.ProfileBonusView.as_view(), name="profile_bonus"),
    url(r'logout-confirm/$', views.ProfileLogoutConfirm.as_view(), name='logout_confirm'),
]
