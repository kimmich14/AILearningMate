from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import User, Profile
from learning.models import Course, Enrollment, Lesson, LessonImage, LessonVideo, ProgressTracking, Quiz
import json

# Create your views here.
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX validation
            data = json.loads(request.body)
            email = data.get('email')
            username = data.get('username')
            
            errors = {}
            if User.objects.filter(email=email).exists():
                errors['email'] = 'This email is already registered'
            if User.objects.filter(username=username).exists():
                errors['username'] = 'This username is already taken'
            
            return JsonResponse({'errors': errors} if errors else {'valid': True})
        
        # Form submission
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        account_type = request.POST.get('account_type')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('usersapp:signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return redirect('usersapp:signup')
        
        try:
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                tutor=(account_type == 'instructor'),
                learner=(account_type == 'learner')
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('usersapp:profile')  # Redirect to profile setup
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('usersapp:signup')
    
    return render(request, 'users/sign_up.html')

@login_required
def profile(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to access your profile')
        return redirect('usersapp:login')

    if request.method == 'POST':
        try:
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.full_name = request.POST.get('full_name', '')
            profile.phone_number = request.POST.get('phone_number', '')
            profile.about = request.POST.get('about', '')
            profile.learning_level = request.POST.get('learning_level', '')

            if 'user_image' in request.FILES:
                profile.user_image = request.FILES['user_image']

            profile.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'valid': True, 'redirect': str(reverse('learningapp:home'))})

            messages.success(request, 'Profile updated successfully!')
            return redirect('learningapp:home')

        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'valid': False, 'error': str(e)})
            messages.error(request, f'Error updating profile: {str(e)}')
            return redirect('usersapp:profile')

    # GET request - show form
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        user_profile = None

    context = {
        'profile': user_profile,
        'learning_levels': ['Beginner', 'Intermediate', 'Advanced', 'Expert']
    }
    return render(request, 'users/profile.html', context)

@csrf_exempt
def user_login(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        if (profile.full_name and profile.phone_number and 
            profile.about and profile.learning_level):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'redirect_url': reverse('learningapp:home')})
            messages.success(request, 'Login successful!')
            return redirect('learningapp:home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)

            redirect_url = reverse('learningapp:home')
            if hasattr(user, 'profile'):
                profile = user.profile
                if not (profile.full_name and profile.phone_number and profile.about and profile.learning_level):
                    redirect_url = reverse('usersapp:profile')

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'redirect_url': redirect_url})
            else:
                return redirect(redirect_url)

        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Invalid email or password'}, status=400)
            else:
                messages.error(request, 'Invalid email or password')
                return redirect('usersapp:login')

    return render(request, 'users/sign_in.html')

@login_required
def dashboard(request):
    # Profile data
    user = request.user
    profile = user.profile
    
    # Dummy learning recommendations
    learning_recommendations = [
        {"title": "Complete Python Basics", "priority": "high", "type": "course"},
        {"title": "Practice Machine Learning Quiz", "priority": "medium", "type": "quiz"},
        {"title": "Review Data Structures", "priority": "low", "type": "review"}
    ]
    
    # Dummy upcoming tasks
    upcoming_tasks = [
        {"title": "Finish Lesson 3: Functions", "due": "Today", "course": "Python Fundamentals"},
        {"title": "Take Week 2 Quiz", "due": "Tomorrow", "course": "Data Science"},
        {"title": "Complete Assignment 1", "due": "In 3 days", "course": "Web Development"}
    ]
    
    # Dummy recent activities
    recent_activities = [
        {"type": "lesson", "title": "Introduction to Pandas", "course": "Data Science", "time": "2 hours ago"},
        {"type": "quiz", "title": "Python Basics Quiz", "score": "85%", "time": "Yesterday"},
        {"type": "course", "title": "Started Web Development", "time": "2 days ago"}
    ]
    
    # Dummy performance data
    performance_data = {
        "strengths": ["Data Analysis", "Python Syntax", "Algorithm Design"],
        "weaknesses": ["Data Visualization", "Statistical Concepts", "Debugging"],
        "progress": {
            "Python Fundamentals": 75,
            "Data Science": 45,
            "Web Development": 20
        }
    }
    
    # Get enrolled courses
    enrolled_courses = Enrollment.objects.filter(user=user).select_related('course')
    
    context = {
        'profile': profile,
        'learning_recommendations': learning_recommendations,
        'upcoming_tasks': upcoming_tasks,
        'recent_activities': recent_activities,
        'performance_data': performance_data,
        'enrolled_courses': enrolled_courses
    }
    return render(request, 'users/dashboard.html', context=context)

@login_required
def instructor_dashboard(request):
    # Instructor personal data
    instructor = request.user
    try:
        profile = instructor.profile
    except Profile.DoesNotExist:
        profile = None
    
    # Get courses taught by this instructor
    courses = Course.objects.filter(instructor=instructor)
    
    # Prepare course data with analytics
    course_data = []
    for course in courses:
        # Get enrollments for this course
        enrollments = Enrollment.objects.filter(course=course)
        enrolled_students = [enrollment.user for enrollment in enrollments]
        
        # Calculate average progress
        progress_data = [enrollment.progress for enrollment in enrollments]
        avg_progress = sum(progress_data) / len(progress_data) if progress_data else 0
        
        # Get progress tracking data for problem areas
        progress_trackings = ProgressTracking.objects.filter(course=course)
        weaknesses = []
        for tracking in progress_trackings:
            if tracking.weaknesses:
                weaknesses.extend(tracking.weaknesses.split(','))
        
        # Count most common weaknesses (problem areas)
        from collections import Counter
        problem_areas = [{"topic": topic.strip(), "students_struggling": count}
                        for topic, count in Counter(weaknesses).most_common(3)]
        
        # AI recommendations (dummy data for now)
        ai_recommendations = [
            f"Consider adding more visual examples for {course.subject} concepts",
            "Students are struggling with basics - suggest prerequisite review",
            "Course might benefit from more interactive exercises"
        ]
        
        # Get course materials
        lessons = Lesson.objects.filter(course=course).order_by('order')
        quizzes = Quiz.objects.filter(lesson__course=course).distinct()
        
        # Get learning materials (images and videos)
        lesson_materials = []
        for lesson in lessons:
            images = LessonImage.objects.filter(lesson=lesson).order_by('order')
            videos = LessonVideo.objects.filter(lesson=lesson).order_by('order')
            lesson_materials.append({
                'lesson': lesson,
                'images': images,
                'videos': videos
            })
        
        course_data.append({
            "course": course,
            "enrolled_students": enrolled_students,
            "enrollments": enrollments,
            "avg_progress": avg_progress,
            "problem_areas": problem_areas,
            "ai_recommendations": ai_recommendations,
            "lessons": lessons,
            "lesson_materials": lesson_materials,
            "quizzes": quizzes,
        })
    
    context = {
        "instructor": instructor,
        "profile": profile,
        "course_data": course_data,
    }
    
    return render(request, 'users/instructor_dashboard.html', context=context)

@login_required
def user_logout(request):
    logout(request)
    return redirect('learningapp:home')

@login_required
def role_redirect_view(request):
    user = request.user

    if user.tutor:
        return redirect('usersapp:instructor_dashboard')  # Replace with your actual tutor dashboard URL name
    elif user.learner:
        return redirect('usersapp:dashboard')  # Replace with your actual learner dashboard URL name
    else:
        # Fallback if no role is set
        return redirect('learningapp:home')