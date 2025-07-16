from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "usersapp"

urlpatterns = [
    path('signup/', views.signup, name='signup'), # Users' registrstion
    path('profile/', views.profile, name='profile'), # User's profile. Can view and update
    path('login/', views.user_login, name='login'), #Users' login
    path('logout/', views.user_logout, name='logout'), # Users' logout
    path('dashboard/', views.dashboard, name='dashboard'), # Leaners' dashboard. Shows all their interaction and learning activities
    path('instructor/', views.instructor_dashboard, name='instructor_dashboard'), # Tutors' dashboard. Shows all their content with CRUD functionalities
    path('redirect/', views.role_redirect_view, name='role_redirect'), # Redirects learnears and tutors to their respective dashboards
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='auth/password_reset.html',
             email_template_name='auth/password_reset_email.html',
             subject_template_name='auth/password_reset_subject.txt'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'),
         name='password_reset_complete'),
]