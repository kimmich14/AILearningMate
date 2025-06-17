from django.urls import path
from . import views

app_name = "learningapp"

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.courses, name='courses'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('ai-tutor/', views.ai_tutor, name='ai_tutor'),
    path('quiz/<int:quiz_id>/', views.quiz, name='quiz'),
    path('progress/', views.progress_tracking, name='progress_tracking'),
    path('assessments/', views.assessments, name='assessments'),
    path('about-us/', views.about_us, name='about_us'),
    path('support/', views.support, name='support'),
    path('submit-discussion/', views.submit_discussion, name='submit_discussion'),
    path('submit-reply/', views.submit_reply, name='submit_reply'),
]