from django.urls import path
from main_app import views


urlpatterns = [
    path('contact/', views.SiteContactView.as_view(), name='contact'),
    # url(r'schedule/$', views.Schedule.as_view(), name='schedule'),
    # url(r'ranklist/$', views.RankList.as_view(), name='ranklist'),
    # url(r'rankilst-detail/(?P<pk>\d+)', views.RankilstUserPoints.as_view(), name='ranklist_detail'),
    # url(r'contact-success/$', views.SiteContactSuccessView.as_view(), name='contacts_success'),
    # url(r'match-detail/(?P<pk>\d+)', views.MatchDetailView.as_view(), name='match_detail'),
]
