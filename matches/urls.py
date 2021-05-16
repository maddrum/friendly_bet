from django.conf.urls import url
from matches import views

app_name = 'matches'
urlpatterns = [
    url(r'prediction/', views.user_predictions_start, name='input_prediction'),
    url(r'prediction-processor/', views.user_predictions_post_handle, name='prediction_processor'),

]
