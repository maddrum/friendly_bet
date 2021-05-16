from django.conf.urls import url
from bonus_points import views

app_name = 'bonus_points'
urlpatterns = [
    # url(r'bonus-main/$', views.BonusMainListView.as_view(), name='bonus_main'),
    # url(r'text/(?P<pk>\d+)$', views.TextInputView.as_view(), name='bonus_input_text'),
    # url(r'number/(?P<pk>\d+)$', views.NumberInputView.as_view(), name='bonus_input_number'),
    # url(r'all-countries/(?P<pk>\d+)$', views.AllCountryInputView.as_view(), name='bonus_input_all_countries'),
    # url(r'choices/(?P<pk>\d+)$', views.SomeChoicesView.as_view(), name='bonus_input_some_countries'),
]
