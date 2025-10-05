from django.contrib import admin
from .models import Course, Meme, Question, Answer, QuizAttempt

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ['text', 'category', 'points']
    list_filter = ['category']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'order', 'created_at']
    list_filter = ['difficulty']

@admin.register(Meme)
class MemeAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'score', 'total_questions', 'category', 'completed_at']
    list_filter = ['category', 'completed_at']