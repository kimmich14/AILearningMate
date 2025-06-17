import random
import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.contrib.auth import get_user_model
from users.models import Profile
from learning.models import (
    Course, Enrollment, Lesson, LessonImage, LessonVideo, Quiz, QuizQuestion,
    UserResponse, QuizResult, Discussion, Reply, ProgressTracking
)
from django.core.files.images import ImageFile

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate dummy data for the platform'

    def handle(self, *args, **kwargs):
        base_path = os.path.dirname(__file__)
        image_files = [f"data{i}.jpg" for i in range(1, 13)]
        user_images = [f"user{i}.jpg" for i in range(1, 7)]

        # --- Users ---
        self.stdout.write('Creating users...')
        users = []
        for i in range(1, 16):
            email = f'user{i}@test.com'
            user = User.objects.create_user(
                email=email,
                username=f'user{i}',
                password='testpass123',
                learner=(i % 2 == 0),
                tutor=(i % 2 != 0)
            )
            # Assign profile image
            profile = user.profile
            profile.full_name = f"Test User {i}"
            profile.phone_number = f"0700000{i:02d}"
            profile.learning_level = random.choice(['Beginner', 'Intermediate', 'Advanced'])
            img_path = os.path.join(base_path, user_images[i % len(user_images)])
            with open(img_path, 'rb') as img_file:
                profile.user_image.save(
                    os.path.basename(img_path),
                    File(img_file)
                )

            profile.save()
            users.append(user)

        # --- Courses ---
        self.stdout.write('Creating courses...')
        courses = []
        for i in range(20):
            instructor = random.choice([u for u in users if u.tutor])
            course = Course.objects.create(
                title=f"Course {i+1}",
                description="This is a sample course description.",
                instructor=instructor,
                subject=random.choice(['Math', 'Science', 'History', 'Tech']),
                difficulty=random.choice(['Beginner', 'Intermediate', 'Advanced']),
                learning_outcomes="Learn a lot of things in this course.",
            )
            img_path = os.path.join(base_path, image_files[i % len(image_files)])
            with open(img_path, 'rb') as img_file:
                course.course_image.save(
                    os.path.basename(img_path),
                    File(img_file)
                )

            courses.append(course)

        # --- Enrollments ---
        self.stdout.write('Creating enrollments...')
        for _ in range(20):
            learner = random.choice([u for u in users if u.learner])
            course = random.choice(courses)
            Enrollment.objects.get_or_create(user=learner, course=course)

        # --- Lessons ---
        self.stdout.write('Creating lessons...')
        lessons = []
        for i in range(50):
            course = random.choice(courses)
            lesson = Lesson.objects.create(
                course=course,
                title=f"Lesson {i+1}",
                content="This is the content of the lesson.",
                order=i % 10
            )
            # Add image
            file_path = os.path.join(base_path, random.choice(image_files))
            with open(file_path, 'rb') as img_file:
                LessonImage.objects.create(
                    lesson=lesson,
                    image=ImageFile(img_file, name=os.path.basename(file_path)),  # ✅ fix applied here
                    caption=f"Image for lesson {i+1}"
                )

            # Add video
            LessonVideo.objects.create(
                lesson=lesson,
                video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
                title="Sample Video",
                description="An embedded sample video."
            )
            lessons.append(lesson)

        # --- Quizzes ---
        self.stdout.write('Creating quizzes...')
        quizzes = []
        for i in range(70):
            lesson = random.choice(lessons)
            quiz = Quiz.objects.create(
                title=f"Quiz {i+1}",
                lesson=lesson,
                description="Quiz description",
                passing_score=random.randint(50, 80),
                max_attempts=random.randint(2, 5),
                time_limit=30,
                difficulty=random.choice(['Easy', 'Medium', 'Hard'])
            )
            quizzes.append(quiz)

        # --- Quiz Questions ---
        self.stdout.write('Creating quiz questions...')
        for i in range(100):
            quiz = random.choice(quizzes)
            QuizQuestion.objects.create(
                quiz=quiz,
                question_text=f"What is {i} + {i}?",
                question_type=random.choice(['MC', 'TF', 'SA']),
                points=random.randint(1, 5),
                explanation="The correct answer is {}.".format(i+i),
                hint="Think about basic addition.",
                order=i % 10
            )

        # --- Discussions and Replies ---
        self.stdout.write('Creating discussions and replies...')
        for _ in range(60):
            lesson = random.choice(lessons)
            user = random.choice(users)
            discussion = Discussion.objects.create(
                lesson=lesson,
                user=user,
                message="This is a discussion message."
            )
            for _ in range(random.randint(0, 4)):
                Reply.objects.create(
                    discussion=discussion,
                    user=random.choice(users),
                    message="Replying to your point."
                )

        # --- Quiz Results & Responses ---
        self.stdout.write('Creating quiz results and responses...')
        for _ in range(15):
            quiz = random.choice(quizzes)
            user = random.choice(users)
            score = random.uniform(30.0, 100.0)
            result = QuizResult.objects.create(
                user=user,
                quiz=quiz,
                attempts=random.randint(1, quiz.max_attempts),
                feedback="Good effort!",
                ai_change="No change needed.",
                hint="Try reviewing lesson notes.",
                score=score,
            )

            for question in quiz.quiz_question.all():
                UserResponse.objects.create(
                    user=user,
                    question=question,
                    response=str(eval(question.explanation.split()[-1])),
                    feedback="Great job!" if score > 60 else "You need to revise.",
                    is_correct=score > 60,
                    points=question.points if score > 60 else 0
                )

        self.stdout.write(self.style.SUCCESS('Dummy data created successfully!'))
