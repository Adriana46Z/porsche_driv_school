from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import random
from django.contrib.auth.models import User

from .models import Course, Meme, Question, Answer, QuizAttempt
from .forms import CustomUserCreationForm, QuizForm


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if email and email.endswith('@instructor.com'):
                messages.error(
                    request,
                    'Email-urile @instructor.com sunt rezervate pentru crearea conturilor de instructor prin panoul de administrare.'
                )
                return render(request, 'registration/register.html', {'form': form})

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

        try:
            user_exists = User.objects.filter(username=username).first()
            if not user_exists:
                user_exists = User.objects.filter(email=username).first()

            if user_exists:
                if user_exists.email and user_exists.email.endswith('@instructor.com'):
                    messages.error(
                        request,
                        'Acces restricționat. Instructorii se autentifică EXCLUSIV prin Panoul de Administrare (/admin).'
                    )
                    return redirect('login')

                if user_exists.is_superuser:
                    messages.error(
                        request,
                        'Administratorii (superuser) se autentifică EXCLUSIV prin Panoul de Administrare (/admin).'
                    )
                    return redirect('login')

                if user_exists.is_staff:
                    messages.error(
                        request,
                        'Utilizatorii cu drepturi de staff se autentifică EXCLUSIV prin Panoul de Administrare (/admin).'
                    )
                    return redirect('login')

        except Exception as e:
            print(f"Eroare la verificare user: {e}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.email and user.email.endswith('@instructor.com'):
                messages.error(
                    request,
                    'Conturile de instructor au acces doar prin Panoul de Administrare. Vă rugăm să folosiți /admin.'
                )
                return redirect('login')

            if user.is_superuser:
                messages.error(
                    request,
                    'Conturile de administrator (superuser) au acces doar prin Panoul de Administrare. Vă rugăm să folosiți /admin.'
                )
                return redirect('login')

            if user.is_staff:
                messages.error(
                    request,
                    'Conturile cu drepturi de staff au acces doar prin Panoul de Administrare. Vă rugăm să folosiți /admin.'
                )
                return redirect('login')

            login(request, user)
            messages.success(request, f'Bun venit, {user.first_name}!')
            return redirect('home')
        else:
            messages.error(request, 'Username sau parolă incorectă')

    return render(request, 'registration/login.html')


def custom_logout(request):
    logout(request)
    messages.success(request, 'Te-ai deconectat cu succes!')
    return redirect('login')


def redirect_if_privileged_user(user):
    if not user.is_authenticated:
        return None

    if (user.email and user.email.endswith('@instructor.com')) or \
            user.is_superuser or \
            user.is_staff:
        return redirect('/admin/')

    return None

def home_view(request):
    if request.user.is_authenticated:
        redirect_response = redirect_if_privileged_user(request.user)
        if redirect_response:
            messages.info(request, 'Redirecționat către Panoul de Administrare.')
            return redirect_response

    courses = Course.objects.all()
    memes = Meme.objects.all().order_by('-created_at')[:6]

    context = {
        'courses': courses,
        'memes': memes,
    }

    if request.user.is_authenticated:
        user_attempts = QuizAttempt.objects.filter(user=request.user)
        total_quizzes = user_attempts.count()
        best_score = user_attempts.order_by('-score').first()

        context.update({"total_quizzes": total_quizzes, "best_score": best_score})

    return render(request, 'home.html', context)


@login_required
def profile_view(request):
    redirect_response = redirect_if_privileged_user(request.user)
    if redirect_response:
        messages.error(request, 'Acces restricționat. Administratorii au acces doar la Panoul de Administrare.')
        return redirect_response

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
    redirect_response = redirect_if_privileged_user(request.user)
    if redirect_response:
        messages.error(request, 'Acces restricționat. Administratorii au acces doar la Panoul de Administrare.')
        return redirect_response

    memes = Meme.objects.all().order_by('-created_at')
    return render(request, 'memes.html', {'memes': memes})


@login_required
def course_detail(request, course_id):
    redirect_response = redirect_if_privileged_user(request.user)
    if redirect_response:
        messages.error(request, 'Acces restricționat. Administratorii au acces doar la Panoul de Administrare.')
        return redirect_response

    course = Course.objects.get(id=course_id)
    related_courses = Course.objects.exclude(id=course_id).filter(difficulty=course.difficulty)[:3]
    return render(request, 'course_detail.html', {
        'course': course,
        'related_courses': related_courses
    })


from django.http import FileResponse
import os


@login_required
def view_pdf(request, course_id):
    redirect_response = redirect_if_privileged_user(request.user)
    if redirect_response:
        messages.error(request, 'Acces restricționat. Administratorii au acces doar la Panoul de Administrare.')
        return redirect_response

    course = Course.objects.get(id=course_id)

    if course.pdf_file and os.path.exists(course.pdf_file.path):
        return FileResponse(open(course.pdf_file.path, 'rb'), content_type='application/pdf')
    else:
        messages.error(request, 'Fișierul PDF nu a fost găsit.')
        return redirect('course_detail', course_id=course_id)

@login_required
def quiz_view(request):
    redirect_response = redirect_if_privileged_user(request.user)
    if redirect_response:
        messages.error(request, 'Acces restricționat. Administratorii au acces doar la Panoul de Administrare.')
        return redirect_response

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
        if len(all_questions) > 24:
            questions = random.sample(all_questions, 24)
        else:
            questions = all_questions

        form = QuizForm(questions=questions)

    return render(request, 'quiz.html', {
        'form': form,
        'questions': questions,
        'total_questions': len(questions),
    })


@login_required
def quiz_history(request):
    redirect_response = redirect_if_privileged_user(request.user)
    if redirect_response:
        messages.error(request, 'Acces restricționat. Administratorii au acces doar la Panoul de Administrare.')
        return redirect_response

    attempts = QuizAttempt.objects.filter(user=request.user)
    return render(request, 'quiz_history.html', {'attempts': attempts})