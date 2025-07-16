from django.urls import path
from . import views

app_name = "learningapp"

urlpatterns = [
    path('', views.home, name='home'), #The homepage
    path('courses/', views.courses, name='courses'), # Lists all available courses
    path('course/<int:course_id>/', views.course_detail, name='course_detail'), #Shows each course's details, has the feature to enroll, and provides enrolled learners with all the course details to learn, take quizzes, and discuss with other enrolled learners
    path('ai-tutor/', views.ai_tutor, name='ai_tutor'), # Helps learners to learn with entirely the help of AI
    path('quiz/<int:quiz_id>/', views.quiz, name='quiz'), # Learners can take quizzes for lessons they learnt
    path('progress/', views.progress_tracking, name='progress_tracking'), # AI helps learners track the progress of their learning
    path('assessments/', views.assessments, name='assessments'), # AI helps assess how students are faring from their quizes performances
    path('about-us/', views.about_us, name='about_us'), # Everything users need to know about this website
    path('support/', views.support, name='support'), # Users can enquire about this website 
    path('submit-discussion/', views.submit_discussion, name='submit_discussion'), # Submits discussion made by learners
    path('submit-reply/', views.submit_reply, name='submit_reply'), # Submits learners' replies to discussions
    path('create-quiz/', views.create_quiz, name='create_quiz'), # Saves quizzes added by tutors
    path('add-question/', views.add_question, name='add_question'), # Saves quiz questions added by tutors
    path('submit-quiz/', views.submit_quiz, name='submit_quiz'), # Learners submit quizes after completion
    path("quiz/<int:quiz_id>/start/", views.start_quiz, name="start_quiz"), # Learners request to retake quizes if they have remaining atttempts
    path("quiz-result/<int:result_id>/pdf/", views.export_quiz_pdf, name="export_quiz_pdf"), # Fetches quiz results for learners and exports them as PDF
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'), # Learners enrollment to courses
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment/callback/', views.mpesa_callback, name='payment_callback'),
    path("payment/status/<int:payment_id>/", views.check_payment_status, name="payment_status"),
]