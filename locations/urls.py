from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # --- 1. TRANG CHỦ & CHI TIẾT ĐỊA ĐIỂM ---
    path('', views.map_view, name='map_home'),
    path('location/<int:pk>/', views.location_detail, name='location_detail'),
    
    # --- 2. HỆ THỐNG TÀI KHOẢN ---
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # --- 3. DASHBOARD QUẢN LÝ (CHÍNH) ---
    path('dashboard/', views.custom_dashboard, name='custom_dashboard'),
    path('dashboard/add/', views.add_location_dashboard, name='add_location'),
    path('dashboard/edit/<int:pk>/', views.edit_location, name='edit_location'),
    path('dashboard/delete/<int:pk>/', views.delete_location_dashboard, name='delete_location'),
    path('dashboard/approve/<int:pk>/', views.approve_location, name='approve_location'),

    # --- 4. QUẢN LÝ NGƯỜI DÙNG (DÀNH CHO ADMIN) ---
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-users/toggle/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),

    # --- 5. HỆ THỐNG KẾT BẠN (CẦN ĐỒNG Ý) ---
    path('friends/find/', views.find_friends, name='find_friends'),
    path('friends/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friends/accept/<int:request_id>/', views.accept_friend_request, name='accept_request'),
    path('friends/reject/<int:request_id>/', views.reject_friend_request, name='reject_request'),

    # --- 6. API DỮ LIỆU (VỊ TRÍ, BẠN BÈ, TRẠNG THÁI) ---
    path('api/update_location/', views.update_location, name='update_location'),
    path('api/update_status/', views.update_status, name='update_status'),
    path('api/friends/', views.get_friends_data, name='get_friends_data'),
]