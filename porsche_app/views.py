from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import random

from .models import Course, Meme, Question, Answer, QuizAttempt
from .forms import CustomUserCreationForm, QuizForm


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cont creat cu succes! Bine ai venit la Porsche School!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bun venit, {user.first_name}!')
            return redirect('home')
        else:
            messages.error(request, 'Username sau parolă incorectă')
    return render(request, 'registration/login.html')


@login_required
def home_view(request):
    courses = Course.objects.all()
    memes = Meme.objects.all().order_by('-created_at')[:6]

    # Statistici utilizator
    user_attempts = QuizAttempt.objects.filter(user=request.user)
    total_quizzes = user_attempts.count()
    best_score = user_attempts.order_by('-score').first()

    context = {
        'courses': courses,
        'memes': memes,
        'total_quizzes': total_quizzes,
        'best_score': best_score,
    }
    return render(request, 'home.html', context)


@login_required
def course_detail(request, course_id):
    course = Course.objects.get(id=course_id)
    related_courses = Course.objects.exclude(id=course_id).filter(difficulty=course.difficulty)[:3]
    return render(request, 'course_detail.html', {
        'course': course,
        'related_courses': related_courses
    })


@login_required
def quiz_view(request):
    # Ia toate întrebările disponibile
    all_questions = list(Question.objects.all())

    if not all_questions:
        messages.info(request, 'Momentan nu sunt întrebări disponibile.')
        return redirect('home')

    if request.method == 'POST':
        form = QuizForm(request.POST, questions=all_questions)
        if form.is_valid():
            score = 0
            total_questions = len(all_questions)

            for question in all_questions:
                field_name = f'question_{question.id}'
                selected_answer = form.cleaned_data[field_name]
                if selected_answer.is_correct:
                    score += question.points

            # Salvează rezultatul
            QuizAttempt.objects.create(
                user=request.user,
                score=score,
                total_questions=total_questions,
                category='general'
            )

            return render(request, 'quiz_result.html', {
                'score': score,
                'total_questions': total_questions,
                'percentage': (score / total_questions) * 100,
                'category': 'general'
            })
    else:
        # Alege 24 de întrebări aleatorii (sau toate dacă sunt mai puține)
        if len(all_questions) > 24:
            questions = random.sample(all_questions, 24)
        else:
            questions = all_questions

        form = QuizForm(questions=questions)

    return render(request, 'quiz.html', {
        'form': form,
        'questions': questions,
        'total_questions': len(questions)
    })


@login_required
def quiz_history(request):
    attempts = QuizAttempt.objects.filter(user=request.user)
    return render(request, 'quiz_history.html', {'attempts': attempts})


@login_required
def profile_view(request):
    user_attempts = QuizAttempt.objects.filter(user=request.user)
    total_quizzes = user_attempts.count()

    if total_quizzes > 0:
        average_score = sum(attempt.score for attempt in user_attempts) / total_quizzes
        best_attempt = user_attempts.order_by('-score').first()
    else:
        average_score = 0
        best_attempt = None

    return render(request, 'profile.html', {
        'total_quizzes': total_quizzes,
        'average_score': average_score,
        'best_attempt': best_attempt,
        'user_attempts': user_attempts[:5]
    })

@login_required
def memes_view(request):
    """Pagina dedicată doar pentru memes"""
    memes = Meme.objects.all().order_by('-created_at')
    return render(request, 'memes.html', {'memes': memes})


from django.http import FileResponse
import os


@login_required
def view_pdf(request, course_id):
    """Vizualizare PDF direct în browser"""
    course = Course.objects.get(id=course_id)

    # Presupunem că PDF-urile sunt în folderul media/courses/
    pdf_path = course.content  # sau alt câmp pentru PDF

    if pdf_path and os.path.exists(pdf_path):
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    else:
        messages.error(request, 'Fișierul PDF nu a fost găsit.')
        return redirect('course_detail', course_id=course_id)

from django.contrib.auth import logout

def custom_logout(request):
    """Logout sigur care funcționează pentru toți utilizatorii"""
    logout(request)
    messages.success(request, 'Te-ai deconectat cu succes!')
    return redirect('login')