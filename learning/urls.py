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
    path('create-quiz/', views.create_quiz, name='create_quiz'),
    path('add-question/', views.add_question, name='add_question'),
    path('submit-quiz/', views.submit_quiz, name='submit_quiz'),
    path("quiz/<int:quiz_id>/start/", views.start_quiz, name="start_quiz"),
    path("quiz-result/<int:result_id>/pdf/", views.export_quiz_pdf, name="export_quiz_pdf"),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
]