from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('quiz/history/', views.quiz_history, name='quiz_history'),
    path('profile/', views.profile_view, name='profile'),

    # ADAUGĂ ASTA pentru a redirecționa /accounts/login/ către /login/
    path('accounts/login/', views.login_view, name='login_redirect'),

    path('memes/', views.memes_view, name='memes'),

    path('course/<int:course_id>/pdf/', views.view_pdf, name='view_pdf'),
]