from django.db import models
from users.models import User

# Create your models here.
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    subject = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=50)
    course_image = models.ImageField(upload_to='courseimages')
    learning_outcomes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_ai_recommended = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrolled_user')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolled_course')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lesson_course')
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
    
class LessonImage(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='lesson_images/', blank=True, null=True)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.lesson.title}"

class LessonVideo(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='videos')
    video_url = models.URLField(blank=True, null=True)  # For embedded videos (YouTube, Vimeo, etc.)
    # OR if you want to host videos yourself:
    video_file = models.FileField(upload_to='lesson_videos/', blank=True, null=True)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Video for {self.lesson.title}"
    
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name='quiz_lesson')
    description = models.TextField(blank=True)
    passing_score = models.PositiveIntegerField(default=70)
    max_attempts = models.PositiveIntegerField(default=3)
    time_limit = models.PositiveIntegerField(help_text="Time limit in minutes", default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    difficulty = models.CharField(max_length=50)

    def __str__(self):
        return self.title
    
class QuizQuestion(models.Model):
    QUESTION_TYPES = [
        ('MC', 'Multiple Choice'),
        ('TF', 'True/False'),
        ('SA', 'Short Answer'),
        ('FB', 'Fill in the Blank'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='quiz_question')
    question_text = models.TextField()
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES, default='MC')
    points = models.PositiveIntegerField(default=1)
    explanation = models.TextField(blank=True, help_text="Explanation of the correct answer")
    hint = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.quiz.title} - Question #{self.order}"
    
class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_response')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='response_question')
    response = models.CharField(max_length=200)
    feedback = models.TextField(blank=True, help_text="Feedback specific to this question")
    is_correct = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question.text}"
    
class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_result')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='quiz_result')
    feedback = models.TextField(blank=True, help_text="Feedback specific to this quiz")
    ai_change = models.TextField(blank=True, help_text="Changes made to this quiz")
    hint = models.TextField(blank=True, help_text="Hint for improvement")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Answer for {self.question.question_text[:50]}"
    
class Discussion(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='discussion_lesson')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussion_user')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"
    
class Reply(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='discussion_reply')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reply_user')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
class ProgressTracking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_user')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progress_course')
    completion_percentage = models.FloatField(default=0.0)
    strengths = models.TextField(null=True, blank=True)
    weaknesses = models.TextField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"