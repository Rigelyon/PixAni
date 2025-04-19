from django.urls import path
from . import views
from .views import anime_search

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('anime/', views.anime_detail, name='anime_detail'),
    path('process_image/', views.process_image, name='process_image'),
    path('anime_search/', views.anime_search, name='anime_search'),
]
