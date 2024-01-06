from django.urls import path
from bonus_points import views

urlpatterns = [
    path("list/", views.BonusMainListView.as_view(), name="bonus_main"),
    path(
        "participate/<int:pk>",
        views.BonusParticipateView.as_view(),
        name="bonus_participate",
    ),
]
