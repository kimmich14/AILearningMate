from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Quiz, QuizQuestion, Lesson, LessonImage, LessonVideo, ProgressTracking, QuizResult, UserResponse, Discussion, Reply, Enrollment, Payment
from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from collections import defaultdict
import json
from django.utils.timezone import now
from difflib import SequenceMatcher
from django.db.models import Avg
from django.db.models import Count, Q
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
import base64, requests
from django.conf import settings
import requests
import datetime
import logging

logger = logging.getLogger(__name__)

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
        'lesson_course__videos',
        'lesson_course__quiz_lesson__quiz_question'
    ), id=course_id)

    lessons = course.lesson_course.all().order_by('order')
    discussions = Discussion.objects.filter(lesson__course=course).select_related('lesson', 'user')

    # Group discussions
    lesson_discussions = defaultdict(list)
    for discussion in discussions:
        lesson_discussions[discussion.lesson_id].append(discussion)

    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()

    context = {
        'course': course,
        'lessons': lessons,
        'lesson_discussions': dict(lesson_discussions),
        'is_enrolled': is_enrolled
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

    avg_completion = user_progress.aggregate(avg=Avg('completion_percentage'))['avg'] or 0

    context = {
        'progress_data': user_progress,
        'avg_completion': round(avg_completion, 2),
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
             to_attr='user_responses')
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
    # Group quiz results by course
    course_quiz_passes = defaultdict(lambda: {'passed': 0, 'total': 0})
    for res in user_results:
        course = res.quiz.lesson.course
        course_quiz_passes[course.id]['total'] += 1
        if res.score >= res.quiz.passing_score:
            course_quiz_passes[course.id]['passed'] += 1

    # Build badges dict
    passed_courses = {
        course_id: data['passed'] == data['total']
        for course_id, data in course_quiz_passes.items()
    }
    average_scores = {}
    for result in user_results:
        quiz_id = result.quiz.id
        if quiz_id not in average_scores:
            avg = QuizResult.objects.filter(quiz_id=quiz_id).aggregate(avg_score=Avg('score'))['avg_score'] or 0
            average_scores[quiz_id] = round(avg, 1)
    context = {
        'user_results': user_results,
        'leaderboards': leaderboards,
        'passed_courses': passed_courses,
        'average_scores': average_scores
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
    
@require_POST
@login_required
def create_quiz(request):
    try:
        lesson = Lesson.objects.get(id=request.POST.get('lesson'))
        quiz = Quiz.objects.create(
            title=request.POST.get('title'),
            lesson=lesson,
            description=request.POST.get('description'),
            passing_score=request.POST.get('passing_score'),
            max_attempts=request.POST.get('max_attempts'),
            time_limit=request.POST.get('time_limit'),
            difficulty=request.POST.get('difficulty'),
        )
        return JsonResponse({'status': 'success', 'quiz_id': quiz.id})
    except Lesson.DoesNotExist:
        return JsonResponse({'error': 'Invalid lesson ID'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@require_POST
@login_required
def add_question(request):
    try:
        quiz = Quiz.objects.get(id=request.POST.get('quiz_id'))
        QuizQuestion.objects.create(
            quiz=quiz,
            question_text=request.POST.get('question_text'),
            question_type=request.POST.get('question_type'),
            points=request.POST.get('points'),
            explanation=request.POST.get('explanation', ''),
            hint=request.POST.get('hint', ''),
            order=request.POST.get('order') or 0
        )
        return JsonResponse({'status': 'success'})
    except Quiz.DoesNotExist:
        return JsonResponse({'error': 'Invalid quiz'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def similarity_score(a, b):
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

@require_POST
@login_required
def submit_quiz(request):
    user = request.user
    try:
        data = json.loads(request.body)
        quiz_id = data['quiz_id']
        answers = data.get('answers', {})
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid input'}, status=400)

    quiz = Quiz.objects.prefetch_related('quiz_question').get(id=quiz_id)
    questions = quiz.quiz_question.all()

    # Check attempts
    result, created = QuizResult.objects.get_or_create(user=user, quiz=quiz)
    if result.attempts >= quiz.max_attempts:
        return JsonResponse({'message': 'You have used all your attempts.'}, status=403)

    result.attempts += 1
    total_score = 0
    total_possible = 0
    feedback_per_question = []

    for question in questions:
        expected = question.explanation or ""
        qid_str = str(question.id)
        response = answers.get(qid_str, "").strip()

        # Default values
        is_correct = False
        points_awarded = 0
        feedback = ""
        correct_answer = expected.split("|")[0].strip()

        if question.question_type == "MC":
            is_correct = response.lower() == correct_answer.lower()
        elif question.question_type == "TF":
            is_correct = response.lower() in ["true", "false"] and response.lower() == correct_answer.lower()
        else:
            # SA or FB
            is_correct = similarity_score(response, correct_answer) >= 0.8

        points_awarded = question.points if is_correct else 0
        total_possible += question.points
        total_score += points_awarded
        feedback = "Correct" if is_correct else f"Expected: {correct_answer}"

        UserResponse.objects.create(
            user=user,
            question=question,
            response=response,
            feedback=feedback,
            is_correct=is_correct,
            points=points_awarded,
            timestamp=now()
        )

        feedback_per_question.append(f"Q{question.id}: {feedback}")

    percentage_score = round((total_score / total_possible) * 100, 2)

    # AI Feedback Logic
    if percentage_score >= quiz.passing_score:
        feedback = "✅ You passed. Great work!"
        ai_change = "None. Quiz is effective."
        hint = "Continue learning and challenge yourself more."
    else:
        feedback = "❌ You didn’t pass. Focus on misunderstood topics."
        ai_change = "Quiz may need easier examples or reordered questions."
        hint = "Review your notes or rewatch key videos in this lesson."

    result.feedback = feedback
    result.ai_change = ai_change
    result.hint = hint
    result.score = percentage_score
    result.created_at = now()
    result.save()
    
    # Determine lesson's course
    course = quiz.lesson.course

    # Update or create progress record
    progress, _ = ProgressTracking.objects.get_or_create(user=user, course=course)

    # Recalculate progress
    all_course_quizzes = Quiz.objects.filter(lesson__course=course).prefetch_related('quiz_result')
    user_results = QuizResult.objects.filter(user=user, quiz__in=all_course_quizzes)

    total_quizzes = all_course_quizzes.count()
    attempted = user_results.count()
    completion_percentage = round((attempted / total_quizzes) * 100, 2) if total_quizzes > 0 else 0

    # Identify strengths and weaknesses
    strong = []
    weak = []
    for r in user_results:
        if r.score >= r.quiz.passing_score:
            strong.append(r.quiz.title)
        else:
            weak.append(r.quiz.title)

    progress.completion_percentage = completion_percentage
    progress.strengths = ", ".join(strong)
    progress.weaknesses = ", ".join(weak)
    progress.save()

    return JsonResponse({
        'message': feedback,
        'score': percentage_score,
        'hint': hint,
        'ai_change': ai_change,
        'question_feedback': feedback_per_question
    })
    
@login_required
def export_quiz_pdf(request, result_id):
    result = get_object_or_404(QuizResult.objects.select_related('quiz', 'user'),
                               id=result_id, user=request.user)
    questions = result.quiz.quiz_question.prefetch_related(
        Prefetch('response_question', queryset=UserResponse.objects.filter(user=request.user),
                 to_attr='user_responses')
    )

    html = render_to_string("learning/pdf_template.html", {
        'result': result,
        'questions': questions,
        'user': request.user,
        'now': now(),
    })

    pdf_file = HTML(string=html).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename=quiz_result_{result.id}.pdf'
    return response

@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz.objects.prefetch_related('quiz_question', 'quiz_question__quiz'), id=quiz_id)
    user = request.user

    # Check attempts
    result, created = QuizResult.objects.get_or_create(user=user, quiz=quiz)
    if not created and result.attempts >= quiz.max_attempts:
        return render(request, "learning/quiz_locked.html", {
            "quiz": quiz,
            "max_attempts": quiz.max_attempts
        })

    return render(request, "learning/take_quiz.html", {
        "quiz": quiz,
        "questions": quiz.quiz_question.all(),
    })
    
@require_POST
@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    Enrollment.objects.get_or_create(user=request.user, course=course)
    return JsonResponse({"message": "Enrolled successfully."})

def send_stk_push(phone, amount, description, payment_id):
    # STEP 1: Generate timestamp and password
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # e.g. 20250716205600
    shortcode = settings.DARAJA_SHORTCODE
    passkey = settings.DARAJA_PASSKEY

    raw_password = shortcode + passkey + timestamp
    password = base64.b64encode(raw_password.encode()).decode()

    # STEP 2: Get access token
    consumer_key = settings.DARAJA_CONSUMER_KEY
    consumer_secret = settings.DARAJA_CONSUMER_SECRET

    auth_response = requests.get(
        "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
        auth=(consumer_key, consumer_secret)
    )

    access_token = auth_response.json().get("access_token")
    if not access_token:
        return {"status": "error", "message": "Failed to get access token"}

    # STEP 3: Prepare STK Push request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(float(amount)),  # Ensure integer
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": settings.DARAJA_CALLBACK_URL,
        "AccountReference": f"Course-{payment_id}",
        "TransactionDesc": description
    }

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        return {"status": "success", "response": response.json()}
    else:
        return {"status": "error", "message": response.text}

@require_POST
@login_required
def process_payment(request):
    user = request.user
    phone = request.POST.get("phone")
    course_id = request.POST.get("course_id")

    if not phone or not course_id:
        return JsonResponse({"status": "error", "message": "Missing phone or course ID"}, status=400)

    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Course not found"}, status=404)

    # Format phone (Safaricom expects 2547XXXXXXXX)
    phone = phone.strip().replace(" ", "")
    if phone.startswith("0"):
        phone = "254" + phone[1:]

    # Create a pending payment record
    payment = Payment.objects.create(
        user=user,
        course=course,
        success=False  # Mark as false until confirmation
    )

    # Trigger STK Push
    response = send_stk_push(phone, course.price, course.title, payment.id)

    if response.get("status") == "success":
        # Save checkout ID to Payment
        payment.checkout_id = response.get("CheckoutRequestID")
        payment.save()
        return JsonResponse({
            "success": True,
            "payment_id": payment.id  # after saving the Payment model
        })
    else:
        return JsonResponse({"status": "error", "message": response.get("message", "STK Push failed")})
    
@csrf_exempt
def mpesa_callback(request):
    try:
        data = json.loads(request.body.decode('utf-8'))

        logger.info("📥 M-Pesa Callback: %s", json.dumps(data, indent=2))
        stk_callback = data.get("Body", {}).get("stkCallback", {})

        result_code = stk_callback.get("ResultCode")
        checkout_id = stk_callback.get("CheckoutRequestID")

        if not checkout_id:
            logger.warning("🚫 Missing CheckoutRequestID in callback.")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Missing checkout ID"}, status=400)

        try:
            payment = Payment.objects.get(checkout_id=checkout_id)
        except Payment.DoesNotExist:
            logger.error("❌ No Payment found with checkout_id=%s", checkout_id)
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Payment not found"}, status=404)

        if result_code == 0:
            # Mark payment as successful
            payment.success = True
            payment.save()

            # Enroll the user in the course
            Enrollment.objects.get_or_create(user=payment.user, course=payment.course)

            logger.info("✅ Payment success recorded. User enrolled.")
        else:
            logger.warning("❌ STK Push failed. ResultCode: %s", result_code)

        return JsonResponse({"ResultCode": 0, "ResultDesc": "Callback handled successfully"})

    except Exception as e:
        logger.exception("💥 Callback processing failed")
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Internal error"}, status=500)

def check_payment_status(request, payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
        if payment.success:
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "pending"})
    except Payment.DoesNotExist:
        return JsonResponse({"status": "failed"})