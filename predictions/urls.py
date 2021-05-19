from django.urls import path
from predictions import views

urlpatterns = [
    path('predict-day/', views.EventCreatePredictionView.as_view(), name='create_predictions'),
    path('predictions-success/', views.PredictionSuccess.as_view(), name='predictions_success'),
    path('update-predicticon/<int:pk>', views.UserUpdatePredictionView.as_view(), name='update_prediction'),
]
