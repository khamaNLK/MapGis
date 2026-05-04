from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # --- TRANG CHỦ & TÀI KHOẢN ---
    path('', views.map_view, name='map_home'),
    path('signup/', views.signup, name='signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # --- ĐĂNG NHẬP / ĐĂNG XUẤT ---
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # ==========================================
    # 🔑 ĐỔI MẬT KHẨU (Custom UI của Khanh)
    # ==========================================
    path('password-change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='registration/password_change_form.html',
             success_url=reverse_lazy('password_change_done')
         ), name='password_change'),

    path('password-change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='registration/password_change_done.html' 
         ), name='password_change_done'),

    # ==========================================
    # 🔐 QUÊN MẬT KHẨU (Custom UI)
    # ==========================================
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             success_url=reverse_lazy('password_reset_done')
         ), name='password_reset'),

    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url=reverse_lazy('password_reset_complete')
         ), name='password_reset_confirm'),

    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), name='password_reset_complete'),

    # --- QUẢN LÝ ĐỊA ĐIỂM (DASHBOARD) ---
    path('location/<int:pk>/', views.location_detail, name='location_detail'),
    
    # 👇 ĐƯỜNG DẪN ĐÁNH GIÁ ĐÃ ĐƯỢC THÊM LẠI 👇
    path('location/<int:pk>/review/', views.add_review, name='add_review'),
    
    path('dashboard/', views.custom_dashboard, name='custom_dashboard'),
    path('dashboard/add/', views.add_location_dashboard, name='add_location'),
    path('dashboard/edit/<int:pk>/', views.edit_location, name='edit_location'),
    path('dashboard/delete/<int:pk>/', views.delete_location_dashboard, name='delete_location'),
    path('dashboard/approve/<int:pk>/', views.approve_location, name='approve_location'),

    # --- BẠN BÈ & API ---
    path('friends/find/', views.find_friends, name='find_friends'),
    path('friends/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friends/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friends/remove/<int:user_id>/', views.remove_friend, name='remove_friend'),
    path('api/update_location/', views.update_location, name='update_location'),
    path('api/friends/', views.get_friends_data, name='get_friends_data'),

    # --- ADMIN ---
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-users/toggle/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('about/', views.about_view, name='about'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)