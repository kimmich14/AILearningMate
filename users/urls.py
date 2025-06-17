from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "usersapp"

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('redirect/', views.role_redirect_view, name='role_redirect'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset.html',
        email_template_name='auth/password_reset_email.html',
        subject_template_name='auth/password_reset_subject.txt'
    ), name='password_reset'),
]