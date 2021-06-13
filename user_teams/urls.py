from django.urls import path

from user_teams import views

urlpatterns = [
    path('list/', views.TeamsListView.as_view(), name='teams_list'),
    path('create/', views.CreateTeamView.as_view(), name='teams_create'),
    path('update/<int:pk>', views.UpdateTeamView.as_view(), name='teams_update'),
    path('update/<int:pk>/members/', views.MembersListView.as_view(), name='team_members'),
    path('join/<uuid:uuid>/', views.JoinTeamView.as_view(), name='team_join'),
    path('link/<int:pk>/', views.TeamInviteLinkView.as_view(), name='team_link'),
    path('approvre/<int:pk>/', views.ApproveMemberDummyView.as_view(), name='approve_member'),
]
