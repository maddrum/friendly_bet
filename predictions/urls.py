from django.urls import path
from predictions import views

urlpatterns = [
    path('predict-day/', views.EventCreatePredictionView.as_view(), name='create_predictions')
]
