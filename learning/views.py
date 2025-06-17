from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Quiz, QuizQuestion, Lesson, LessonImage, LessonVideo, ProgressTracking, QuizResult, UserResponse, Discussion, Reply
from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from collections import defaultdict

def home(request):
    return render(request, 'learning/home.html')

def courses(request):
    courses = Course.objects.all()
    context = {
        'courses': courses,
    }
    return render(request, 'learning/courses.html', context=context)

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course.objects.prefetch_related(
        'lesson_course__images',
        'lesson_course__videos'
    ), id=course_id)
    
    lessons = course.lesson_course.all().order_by('order')
    discussions = Discussion.objects.filter(lesson__course=course).select_related('lesson', 'user')

    # Group discussions by lesson ID
    lesson_discussions = defaultdict(list)
    for discussion in discussions:
        lesson_discussions[discussion.lesson_id].append(discussion)

    context = {
        'course': course,
        'lessons': lessons,
        'lesson_discussions': dict(lesson_discussions),  # cast to normal dict for templates
    }
    return render(request, 'learning/course.html', context)

@login_required
def ai_tutor(request):
    return render(request, 'learning/ai_tutor.html')

@login_required
def quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    questions = quiz.quiz_question.all()
    context = {
        'quiz': quiz,
        'questions': questions
    }
    return render(request, 'learning/quiz.html', context=context)

@login_required
def progress_tracking(request):
    user_progress = ProgressTracking.objects.filter(
        user=request.user
    ).select_related('course').order_by('-last_accessed')
    
    context = {
        'progress_data': user_progress
    }
    return render(request, 'learning/progress_tracking.html', context=context)

@login_required
def assessments(request):
    # Get all quiz results for the current user
    user_results = QuizResult.objects.filter(
        user=request.user
    ).select_related('quiz').prefetch_related(
        Prefetch('quiz__quiz_question__response_question', 
                queryset=UserResponse.objects.filter(user=request.user),
                to_attr='user_responses'
        )
    ).order_by('-created_at')
    
    # Get leaderboard data for each quiz
    leaderboards = {}
    for result in user_results:
        if result.quiz_id not in leaderboards:
            leaders = QuizResult.objects.filter(
                quiz=result.quiz
            ).select_related('user').order_by('-score')[:10]
            leaderboards[result.quiz_id] = [
                {'position': i+1, 'data': leader} 
                for i, leader in enumerate(leaders)
            ]
    
    context = {
        'user_results': user_results,
        'leaderboards': leaderboards,
    }
    return render(request, 'learning/assessments.html', context=context)

def about_us(request):
    return render(request, 'learning/about_us.html')

def support(request):
    return render(request, 'learning/support.html')

@require_POST
@login_required
def submit_discussion(request):
    lesson_id = request.POST.get("lesson_id")
    message = request.POST.get("message")

    try:
        lesson = Lesson.objects.get(id=lesson_id)
        Discussion.objects.create(
            lesson=lesson,
            user=request.user,
            message=message
        )
        return JsonResponse({"status": "success"}, status=200)
    except Lesson.DoesNotExist:
        return JsonResponse({"error": "Lesson not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@require_POST
@login_required
def submit_reply(request):
    discussion_id = request.POST.get("discussion_id")
    message = request.POST.get("message")

    try:
        discussion = Discussion.objects.get(id=discussion_id)
        Reply.objects.create(
            discussion=discussion,
            user=request.user,
            message=message
        )
        return JsonResponse({'status': 'success'}, status=200)
    except Discussion.DoesNotExist:
        return JsonResponse({'error': 'Discussion not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)