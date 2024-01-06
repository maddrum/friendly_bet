from django.urls import path

from ranklists import views

urlpatterns = [
    path("", views.RankListView.as_view(), name="ranklist"),
    path("gin/balance/", views.GinPointsMatchesView.as_view(), name="gin_total"),
    path("gin/users/", views.GinPointsUsersView.as_view(), name="gin_users"),
    path("gin/usages/", views.GinPointsNumberOfUsagesView.as_view(), name="gin_usages"),
    path(
        "detail/<int:pk>",
        views.RankilstUserPointsView.as_view(),
        name="ranklist_detail",
    ),
]
