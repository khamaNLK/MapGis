from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, name='map_home'),
    path('add/', views.add_location, name='add_location'),
]