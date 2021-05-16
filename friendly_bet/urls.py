from django.contrib import admin
from django.conf.urls import url, include
from main_app import views

urlpatterns = [
    url(r'^$', views.Index.as_view(), name='index'),
    url(r'main/', include('main_app.urls', namespace='main_app')),
    url(r'accounts/', include('accounts.urls', namespace='accounts')),
    url(r'matches/', include('matches.urls', namespace='matches')),
    url(r'bonus/', include('bonus_points.urls', namespace='bonus_points')),
    url(r'stats/', include('site_stats.urls', namespace='site_stats')),
    url('admin/', admin.site.urls),
]
