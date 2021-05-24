# import debug_toolbar

from django.contrib import admin
from django.urls import include, path

from main_app import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('main/', include('main_app.urls')),
    path('accounts/', include('accounts.urls')),
    path('matches/', include('matches.urls')),
    path('predictions/', include('predictions.urls')),
    path('bonus/', include('bonus_points.urls')),
    path('klimatik/', admin.site.urls),

    # path('__debug__/', include(debug_toolbar.urls)),
]
