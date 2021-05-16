from django.views.generic import TemplateView, ListView
from site_stats.models import TotalStats, UserGuessesNumber
from matches.models import UserPredictions
from matches.models import EventDates
from django.utils import timezone
import datetime
from django.contrib.auth import get_user_model
# for fusion charts
from fusioncharts.fusioncharts import FusionCharts


class StatsTextStatsView(TemplateView):
    template_name = 'site_stats/text-stats.html'

    def get_context_data(self, **kwargs):
        # return data from total
        context = super().get_context_data()
        all_stats = TotalStats.objects.all().order_by('-created_date')
        user_most_match_states = UserGuessesNumber.objects.all().order_by('-guessed_matches')[0]
        user_most_results = UserGuessesNumber.objects.all().order_by('-guessed_results')[0]
        latest_stats = all_stats[0]
        # convert created date into Sofia time
        timezone_sofia = timezone.get_default_timezone()
        utc_created_time = timezone.utc.localize(latest_stats.created_date, is_dst=None)
        sofia_created_time = utc_created_time.astimezone(timezone_sofia)
        # add some context
        context['total_predicioons'] = latest_stats.total_predictions
        context['total_points_gained'] = latest_stats.total_points_gained
        context['total_match_states_guessed'] = latest_stats.total_match_states_guessed
        context['total_match_results_guessed'] = latest_stats.total_match_results_guessed
        context['date'] = sofia_created_time
        context['user_most_match_states'] = user_most_match_states
        context['user_most_match_states_id'] = user_most_match_states.user.id
        context['user_most_results'] = user_most_results
        context['user_most_results_id'] = user_most_results.user.id

        return context


class CommonChartsBaseByDays(TemplateView):
    # not to be used alone. Base for other stats classes
    # Determines dates range
    # Sets graphics
    template_name = 'site_stats/stats-common.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        all_events = EventDates.objects.all()
        event_dates = {item.event_name: [item.event_start_date, item.event_end_date,
                                         (item.event_end_date - item.event_start_date).days] for item in
                       all_events}

        data_source = {}
        data_source['chart'] = {
            "labelFontSize": 12,
            "theme": "zune"
        }
        data_source['data'] = []
        context['data_source'] = data_source
        context['event_dates'] = event_dates
        return context


class CommonPredictionChart(CommonChartsBaseByDays):

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        graph_name = 'Дадени прогнози по дни'
        event_dates = context['event_dates']
        data_source = context['data_source']
        data_source['data'] = []
        for item in event_dates.values():
            start_date = item[0]
            difference = item[2]
            for day in range(difference + 1):
                query_date = start_date + datetime.timedelta(days=day)
                day_prediction_count = UserPredictions.objects.filter(match__match_date=query_date).count()
                legend_date = str(query_date).split('-')[2] + "." + str(query_date).split('-')[1]
                temp_dict = {
                    "label": str(legend_date),
                    "value": day_prediction_count,
                }
                data_source['data'].append(temp_dict)
            break
            # only first event will be shown. If we have to add future stats for multiple events this should be changed accordingly
        column2d = FusionCharts("column2d", "ex1", "1000", "600", "chart-1", "json", data_source)
        context['output'] = column2d.render()
        context['graph_name'] = graph_name
        return context


class CommonPointsChart(CommonChartsBaseByDays):

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        graph_name = 'Спечелени точки по дни'
        event_dates = context['event_dates']
        data_source = context['data_source']
        data_source['data'] = []
        for item in event_dates.values():
            start_date = item[0]
            end_date = item[1]
            difference = item[2]
            for day in range(difference + 1):
                query_date = start_date + datetime.timedelta(days=day)
                day_points_objects = UserPredictions.objects.filter(match__match_date=query_date).values_list(
                    'points_gained', flat=True)
                points_sum = sum(day_points_objects)
                legend_date = str(query_date).split('-')[2] + "." + str(query_date).split('-')[1]
                temp_dict = {
                    "label": str(legend_date),
                    "value": points_sum,
                }
                data_source['data'].append(temp_dict)
            break
            # only first event will be shown. If we have to add future stats for multiple events this should be changed accordingly

        column2d = FusionCharts("column2d", "ex1", "1000", "600", "chart-1", "json", data_source)
        context['graph_name'] = graph_name
        context['output'] = column2d.render()
        return context


class AllUsersListView(ListView):
    model = get_user_model()
    ordering = ('username')
    template_name = 'site_stats/user-selector.html'
    context_object_name = 'all_users'


class UserGraphsView(CommonChartsBaseByDays):
    template_name = 'site_stats/user-graphs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user_id = self.kwargs['pk']
        username = get_user_model().objects.get(id=user_id).username
        event_dates = context['event_dates']
        data_source_points = dict(context['data_source'])
        data_source_points['data'] = []
        data_source_predictions = dict(context['data_source'])
        data_source_predictions['data'] = []
        # get predictions for user
        for item in event_dates.values():
            start_date = item[0]
            difference = item[2]
            for day in range(difference + 1):
                query_date = start_date + datetime.timedelta(days=day)
                day_prediction_count = UserPredictions.objects.filter(user_id=user_id,
                                                                      match__match_date=query_date).count()
                legend_date = str(query_date).split('-')[2] + "." + str(query_date).split('-')[1]
                temp_dict = {
                    "label": str(legend_date),
                    "value": day_prediction_count,
                }
                data_source_predictions['data'].append(temp_dict)
            break
        column2d_predictions = FusionCharts("column2d", "ex1", "1000", "600", "chart-predictions", "json",
                                            data_source_predictions)
        context['graph_name_predictions'] = f'Прогнози по дни за {username}'
        context['output_predictions'] = column2d_predictions.render()

        # get user points by days
        for item in event_dates.values():
            start_date = item[0]
            difference = item[2]
            for day in range(difference + 1):
                query_date = start_date + datetime.timedelta(days=day)
                day_points_objects = UserPredictions.objects.filter(match__match_date=query_date,
                                                                    user_id=user_id).values_list(
                    'points_gained', flat=True)
                points_sum = sum(day_points_objects)
                legend_date = str(query_date).split('-')[2] + "." + str(query_date).split('-')[1]
                temp_dict = {
                    "label": str(legend_date),
                    "value": points_sum,
                }
                data_source_points['data'].append(temp_dict)
            break
        column2d_points = FusionCharts("column2d", "ex2", "1000", "600", "chart-points", "json", data_source_points)
        context['graph_name_points'] = f'Точки по дни за {username}'
        context['output_points'] = column2d_points.render()

        return context
