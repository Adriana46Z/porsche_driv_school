from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='courses_pdf/', blank=True, null=True)  # ✅ ADAUGĂ ASTA
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0)
    difficulty = models.CharField(max_length=20, choices=[
        ('beginner', 'Începător'),
        ('intermediate', 'Intermediar'),
        ('advanced', 'Avansat')
    ], default='beginner')

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title

class Meme(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='memes/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    text = models.TextField()
    image = models.ImageField(upload_to='questions/', blank=True, null=True)
    points = models.IntegerField(default=1)
    category = models.CharField(max_length=50, choices=[
        ('traffic', 'Legislație Trafic'),
        ('signs', 'Indicații Rutiere'),
        ('safety', 'Siguranță Rutieră'),
        ('porsche', 'Cunoștințe Porsche')
    ], default='traffic')

    def __str__(self):
        return f"{self.get_category_display()}: {self.text[:50]}..."

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.text[:30]} - {self.text}"

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, default='general')

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.score}/{self.total_questions} ({self.category})"

    def has_pdf(self):  # ✅ ADAUGĂ METODA ASTA
        return bool(self.pdf_file)