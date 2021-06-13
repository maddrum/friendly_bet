from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.urls.exceptions import Http404
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from user_teams import forms
from user_teams.models import TeamMember, UserTeam


class TeamsListView(LoginRequiredMixin, ListView):
    template_name = 'user_teams/teams-list.html'
    context_object_name = 'teams'

    def get_queryset(self):
        qs = TeamMember.objects.filter(user=self.request.user)
        return qs

    def get_context_data(self, object_list=None, **kwargs):
        context = super(TeamsListView, self).get_context_data(object_list=object_list, **kwargs)
        context['your_teams'] = UserTeam.objects.filter(founder=self.request.user)
        return context


class CreateTeamView(LoginRequiredMixin, CreateView):
    template_name = 'user_teams/create-team.html'
    model = UserTeam
    form_class = forms.CreateUpdateTeamForm
    success_url = reverse_lazy('teams_list')

    def form_valid(self, form):
        form.instance.founder = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        # create team member
        team_member, created = TeamMember.objects.get_or_create(user=self.request.user, team=self.object)
        team_member.approved = True
        team_member.save()
        return super().get_success_url()


class UpdateTeamView(LoginRequiredMixin, UpdateView):
    template_name = 'user_teams/create-team.html'
    model = UserTeam
    form_class = forms.CreateUpdateTeamForm
    success_url = reverse_lazy('teams_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.founder != self.request.user:
            raise Http404()
        return obj


class MembersListView(LoginRequiredMixin, TemplateView):
    template_name = 'user_teams/members-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = get_object_or_404(UserTeam, pk=self.kwargs['pk'])
        if team.founder != self.request.user:
            raise Http404()
        team_members = team.team_team.all()
        context['team'] = team
        context['team_members'] = team_members
        return context


class TeamInviteLinkView(LoginRequiredMixin, TemplateView):
    template_name = 'user_teams/join-link.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = get_object_or_404(UserTeam, pk=self.kwargs['pk'])
        if team.founder != self.request.user:
            raise Http404()
        link = reverse_lazy('team_join', kwargs={'uuid': str(team.uuid)})
        context['link'] = link
        return context


class ApproveMemberDummyView(LoginRequiredMixin, TemplateView):
    def dispatch(self, request, *args, **kwargs):
        member = get_object_or_404(TeamMember, pk=self.kwargs['pk'])
        if member.team.founder != self.request.user:
            raise Http404()
        member.approved = True
        member.save()
        return redirect(reverse_lazy('team_members', kwargs={'pk': member.team.pk}))


class JoinTeamView(LoginRequiredMixin, TemplateView):
    template_name = 'user_teams/join_success.html'

    def dispatch(self, request, *args, **kwargs):
        team = get_object_or_404(UserTeam, uuid=self.kwargs['uuid'])
        member, created = TeamMember.objects.get_or_create(team=team, user=self.request.user)
        if not created:
            return redirect('teams_list')
        return super().dispatch(request, *args, **kwargs)
