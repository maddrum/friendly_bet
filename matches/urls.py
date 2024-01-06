from django.urls import path
from matches import views

urlpatterns = [
    path("schedule/", views.ScheduleView.as_view(), name="schedule"),
    path("detail/<int:pk>", views.MatchDetailView.as_view(), name="match_detail"),
]
