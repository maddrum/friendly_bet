from django.urls import path
from matches import views

urlpatterns = [
    path('schedule/', views.ScheduleView.as_view(), name='schedule')
    # url(r'prediction/', views.user_predictions_start, name='input_prediction'),
    # url(r'prediction-processor/', views.user_predictions_post_handle, name='prediction_processor'),

]
