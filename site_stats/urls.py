from django.conf.urls import url
from site_stats import views

app_name = 'site_stats'
urlpatterns = [
    url(r'text-stats/$', views.StatsTextStatsView.as_view(), name='text_stats'),
    url(r'prediction-chart/$', views.CommonPredictionChart.as_view(), name='prediction_chart'),
    url(r'points-chart/$', views.CommonPointsChart.as_view(), name='prediction_points'),
    url(r'users-selector/$', views.AllUsersListView.as_view(), name='user_selector'),
    url('user-graphs/(?P<pk>\d+)', views.UserGraphsView.as_view(), name='graphs_per_user'),
]
