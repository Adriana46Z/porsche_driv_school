import os
import django
import sys

# Configurează Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'porsche_school.settings')
django.setup()

from porsche_app.models import Course, Meme, Question, Answer
from django.core.files import File


def load_courses_from_folder(folder_path):
    """Încarcă cursuri din fișierele .txt sau .pdf dintr-un folder"""
    for filename in os.listdir(folder_path):
        if filename.endswith(('.txt', '.pdf')):
            file_path = os.path.join(folder_path, filename)
            title = os.path.splitext(filename)[0].replace('_', ' ').title()

            if filename.endswith('.txt'):
                # Pentru fișiere text, citește conținutul
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read().strip()

                pdf_file = None
            else:
                # Pentru PDF, pune un mesaj simplu în content
                content = f"Curs: {title}\n\nAcest curs este disponibil în format PDF cu imagini și formatare completă."
                pdf_file = file_path

            # Determină dificultatea
            difficulty = 'beginner'
            if 'avansat' in filename.lower():
                difficulty = 'advanced'
            elif 'intermediar' in filename.lower():
                difficulty = 'intermediate'

            # Creează sau actualizează cursul
            course, created = Course.objects.get_or_create(
                title=title,
                defaults={'content': content, 'difficulty': difficulty}
            )

            # Dacă este PDF, încarcă fișierul
            if filename.endswith('.pdf') and pdf_file:
                with open(pdf_file, 'rb') as f:
                    course.pdf_file.save(filename, File(f))
                    course.save()
                print(f"✅ Curs PDF creat: {title} ({difficulty}) - Fișier PDF încărcat")
            elif created:
                print(f"✅ Curs text creat: {title} ({difficulty})")


def load_memes_from_folder(folder_path):
    """Încarcă memes din imagini dintr-un folder"""
    supported_formats = ('.jpg', '.jpeg', '.png', '.gif')

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(supported_formats):
            file_path = os.path.join(folder_path, filename)
            title = os.path.splitext(filename)[0].replace('_', ' ').title()

            with open(file_path, 'rb') as file:
                meme, created = Meme.objects.get_or_create(title=title)
                if created or not meme.image:
                    meme.image.save(filename, File(file))
                    print(f"✅ Meme încărcat: {title}")


def load_questions_from_folder(folder_path):
    """Încarcă întrebări și răspunsuri din fișiere text"""
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)

            with open(file_path, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]

                if len(lines) >= 5:  # Întrebare + 4 răspunsuri
                    question_text = lines[0]

                    # Determină categoria din nume sau conținut
                    category = 'traffic'
                    if 'porsche' in filename.lower():
                        category = 'porsche'
                    elif 'semne' in filename.lower() or 'signs' in filename.lower():
                        category = 'signs'
                    elif 'siguranta' in filename.lower() or 'safety' in filename.lower():
                        category = 'safety'

                    question, created = Question.objects.get_or_create(
                        text=question_text,
                        category=category
                    )

                    if created:
                        # Adaugă răspunsurile (ultimul este corect)
                        for i, answer_text in enumerate(lines[1:5]):
                            is_correct = (i == 3)  # Ultimul răspuns este corect
                            Answer.objects.create(
                                question=question,
                                text=answer_text,
                                is_correct=is_correct
                            )
                        print(f"✅ Întrebare încărcată: {question_text[:50]}... ({category})")


def main():
    """Funcția principală pentru încărcarea datelor"""
    base_path = os.path.dirname(os.path.abspath(__file__))

    # Modifică aceste căi cu locațiile folderelor tale
    courses_folder = os.path.join(base_path, 'data', 'courses')
    memes_folder = os.path.join(base_path, 'data', 'memes')
    questions_folder = os.path.join(base_path, 'data', 'questions')

    # Creează folderele dacă nu există
    os.makedirs(courses_folder, exist_ok=True)
    os.makedirs(memes_folder, exist_ok=True)
    os.makedirs(questions_folder, exist_ok=True)

    print("🚀 Încep încărcarea datelor în Porsche School...")

    # Încarcă datele
    load_courses_from_folder(courses_folder)
    load_memes_from_folder(memes_folder)
    load_questions_from_folder(questions_folder)

    print("🎉 Încărcarea datelor s-a finalizat cu succes!")
    print("\n📁 Structura așteptată pentru foldere:")
    print("data/")
    print("├── courses/       # .txt sau .pdf files")
    print("├── memes/         # .jpg, .jpeg, .png, .gif")
    print("└── questions/     # .txt files (întrebare + 4 răspunsuri)")


if __name__ == "__main__":
    main()