from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from accounts import views

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('register-success/', views.UserRegisterSuccessView.as_view(), name='register_success'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='../thank-you'), name='logout'),
    path('thank-you/', views.ThankYouView.as_view(), name='thank_you'),
    path('profile/', views.UserPredictionsListView.as_view(), name='profile'),
    # url(r'profile-match-update/(?P<pk>\d+)', views.UserUpdatePredictionView.as_view(), name='update_prediction'),
    path('profile-history-and-points/', views.ProfilePredictionStats.as_view(), name='profile_history'),
    path('profile-settings/', views.UserSettingsUpdateView.as_view(), name='profile_settings'),
    # url(r'settings-success/$', views.SettingsSuccess.as_view(), name='settings_success'),
    # url(r'profile-password-change/$',
    #     PasswordChangeView.as_view(template_name='accounts/password-change.html', success_url='../login'),
    #     name='password_change'),
    # url(r'bonuses/$', views.ProfileBonusView.as_view(), name="profile_bonus"),
    path('logout-confirm/', views.ProfileLogoutConfirm.as_view(), name='logout_confirm'),
]
