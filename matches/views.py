from django.shortcuts import render
from matches.models import UserPredictions, Matches, EventDates
import datetime
from django.middleware.csrf import CsrfViewMiddleware
from django.contrib.auth.decorators import login_required


@login_required
def user_predictions_start(request):
    error_text = ''
    show_back_button = True
    user_id = request.user
    event_name = 'World Cup 2018'

    # date and datetime formats and WC start date
    date_format = '%Y-%m-%d'
    datetime_format = date_format + ' ' + '%H:%M:%S'
    start_date = EventDates.objects.get(event_name=event_name).event_start_date
    # get current date and today match or first match if before start date
    date_difference = datetime.datetime.now().date() - start_date
    print(date_difference)
    if date_difference.days < 0:
        date = start_date
    else:
        date = datetime.datetime.now().date()
    utc_current_time_delta = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)

    # # test
    # test_days = 1
    # test_days1 = test_days
    # test_hours = -8
    # test_minutes = 0
    # test_timedelta = datetime.timedelta(days=test_days, minutes=test_minutes, hours=test_hours)
    # test_timedelta1 = datetime.timedelta(days=test_days1)
    # utc_current_time_delta = utc_current_time_delta + test_timedelta
    # date = date + test_timedelta1
    # print(date)
    # print(utc_current_time_delta)
    # # end test

    today_match = Matches.objects.filter(match_date=date, match_start_time_utc__gte=utc_current_time_delta)

    # A check if user already gave prediction for that day
    for item in today_match:
        match_id = item.pk
        user_filter = UserPredictions.objects.filter(match=match_id, user_id=user_id)
        for result in user_filter:
            if result.gave_prediction:
                show_back_button = False
                error_text = 'Вече си дал твоите прогнози за деня! ' \
                             'Ако искаш да ги промениш, отиди в твоя профил /с мишката нагоре, менюто, ЦЪК-ЦЪК-ГОТОВО/'
    if error_text:
        content_dict = {
            'error_text': error_text,
            'show_back_button': show_back_button,
        }
        return render(request, 'matches/prediction-error.html', content_dict)
    else:
        content_dict = {
            'form': today_match,
            'date': date,
        }
        return render(request, 'matches/input-prediction.html', content_dict)


@login_required
def user_predictions_post_handle(request):
    user_id = request.user
    error_text = ''
    state = ''
    goals_home = 0
    goals_guest = 0
    has_error = False
    show_back_button = True
    tie_statuses = ['tie', 'penalties_home', 'penalties_guest']
    # check if there is form POST
    if request.method != 'POST':
        error_text = 'Невалидна форма! Върни се в началото!'
        show_back_button = False
        content_dict = {
            'error_text': error_text,
            'show_back_button': False,
        }
        return render(request, 'matches/prediction-error.html', content_dict)
    # check if user have predictions for that day already
    date_check = datetime.datetime.now().date()
    check_queryset = UserPredictions.objects.filter(match__match_date=date_check, user_id=user_id).count()
    if check_queryset != 0:
        error_text = 'Вече има прогнози за този ден от теб!'
        show_back_button = False
        content_dict = {
            'error_text': error_text,
            'show_back_button': False,
        }
        return render(request, 'matches/prediction-error.html', content_dict)
    # CSRF TOKEN manual check
    reason = CsrfViewMiddleware().process_view(request, None, (), {})
    if reason:
        raise PermissionError()
    # handle POST data and check for errors
    post_data = dict(request.POST)
    post_data = {key: value for key, value in post_data.items() if key != 'csrfmiddlewaretoken'}
    predict_match_data = {}
    # check if data input is okay
    for key in post_data:
        split_key = key.split('_')
        match_number = int(split_key[0])
        if split_key[1] == 'match':
            state = post_data[key][0]
        elif split_key[2] == 'home':
            try:
                goals_home = int(post_data[key][0])
            except ValueError:
                error_text = "Моля, въведете цели положителни числа в полетата за гол! Като бройка голове - един, два, три... Опитай пак!"
                has_error = True
                break
        elif split_key[2] == 'guest':
            try:
                goals_guest = int(post_data[key][0])
            except ValueError:
                error_text = 'Моля, въведете цели положителни числа в полетата за гол! Като бройка голове - един, два, три... Опитай пак!'
                has_error = True
                break
        if goals_guest < 0 or goals_home < 0:
            error_text = 'Моля, въведете цели положителни числа в полетата за гол! Като бройка голове - един, два, три... Опитай пак!'
            has_error = True
            break
        temp_arr = [state, goals_home, goals_guest]
        predict_match_data[match_number] = temp_arr

    # check if data is logically correct
    if not has_error:
        for key in predict_match_data:
            state = predict_match_data[key][0]
            goals_home = predict_match_data[key][1]
            goals_guest = predict_match_data[key][2]
            if state == 'home' and goals_home <= goals_guest:
                error_text = f'Головете за мач {key} не съотвестват на въведения изход от двубоя. Въведена е победа за домакин, ' \
                             'но головете на домакина по-малко от тези на госта!'
                has_error = True
            elif state == 'guest' and goals_guest <= goals_home:

                error_text = f'Головете за мач {key} не съотвестват на въведения изход от двубоя. Въведена е победа за гост, ' \
                             'но головете на госта по-малко от тези на домакина!'
                has_error = True
            elif state in tie_statuses and goals_home != goals_guest:
                error_text = f'Головете мач {key} на домакина и на госта не са равни!'
                has_error = True

    # write to database
    for key in predict_match_data:
        if has_error:
            break
        match_state = predict_match_data[key][0]
        goals_home = predict_match_data[key][1]
        goals_guest = predict_match_data[key][2]
        match = Matches.objects.get(match_number=key)
        # check if match has started!
        current_time = datetime.datetime.utcnow()
        if current_time > match.match_start_time_utc:
            print(f'NOTE: {request.user} tried to give prediction for {match} at UTC: {current_time}')
            has_error = True
            error_text = error_text + f'|||Твоята прогноза за {match} не беше зачетена, тъй като мача е вече започнал.|||'
            show_back_button = False
            continue
        user_prediction = UserPredictions(user_id=user_id, match=match, prediction_match_state=match_state,
                                          prediction_goals_home=goals_home, prediction_goals_guest=goals_guest,
                                          gave_prediction=True, creation_time=datetime.datetime.utcnow(),
                                          last_edit=datetime.datetime.utcnow())
        user_prediction.save()

    if has_error:
        content_dict = {
            'error_text': error_text,
            'show_back_button': show_back_button,
        }
        return render(request, 'matches/prediction-error.html', content_dict)
    else:
        content_dict = {}
        return render(request, 'matches/prediction-success.html', content_dict)
