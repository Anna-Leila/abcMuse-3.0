from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePage, name='home-page'),
    path('play/', views.playingField, name = 'playing-field')
]
