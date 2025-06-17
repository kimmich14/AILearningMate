from django.contrib import admin
from .models import Course, Enrollment, Lesson, LessonImage, LessonVideo, Quiz, QuizQuestion, UserResponse, Discussion, ProgressTracking

# Register your models here.
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Lesson)
admin.site.register(LessonImage)
admin.site.register(LessonVideo)
admin.site.register(Quiz)
admin.site.register(QuizQuestion)
admin.site.register(UserResponse)
admin.site.register(Discussion)
admin.site.register(ProgressTracking)