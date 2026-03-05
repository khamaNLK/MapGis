from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.map_view, name='map_home'),
    path('add/', views.add_location, name='add_location'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('location/<int:pk>/', views.location_detail, name='location_detail'),
    path('location/<int:pk>/edit/', views.edit_location, name='edit_location'),
    path('location/<int:pk>/delete/', views.delete_location, name='delete_location'),
    path('api/update_location/', views.update_location, name='update_location'),
    path('api/friends/', views.get_friends_data, name='get_friends_data'),
    path('api/update_status/', views.update_status, name='update_status'),
]
