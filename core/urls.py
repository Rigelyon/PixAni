from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('anime/', views.anime_detail, name='anime_detail'),
    path('process_image/', views.process_image, name='process_image'),
]
