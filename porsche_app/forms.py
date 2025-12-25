from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Question


# ============================================
# 1. FORMULARE PENTRU USER
# ============================================

class CustomUserCreationForm(UserCreationForm):
    """Formular pentru înregistrare utilizatori (pentru register.html) - BLOCHEAZĂ instructorii"""
    email = forms.EmailField(
        required=True,
        label=_("Email"),
        help_text=_("Obligatoriu. Folosiți un email valid.")
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label=_("Prenume")
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label=_("Nume")
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # ✅ BLOCHEAZĂ COMPLET înregistrarea cu email de instructor
        if email and email.endswith('@instructor.com'):
            raise ValidationError(
                _("Email-urile @instructor.com sunt rezervate pentru crearea conturilor de instructor prin panoul de administrare.")
            )
        return email

    def clean(self):
        """Validare suplimentară"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if email and email.endswith('@instructor.com'):
            raise ValidationError(
                _("Nu puteți crea cont cu adresă de instructor. Această funcționalitate este disponibilă doar pentru administratori.")
            )
        return cleaned_data


class AdminUserCreationForm(UserCreationForm):
    """Formular pentru crearea utilizatorilor în admin - VERSIUNE CORECTĂ"""

    username = forms.CharField(
        label=_("Nume utilizator"),
        max_length=150,
        help_text=_("Obligatoriu. 150 de caractere sau mai puține. Numai litere, cifre și @/./+/-/_."),
        error_messages={
            'required': _("Acest câmp este obligatoriu."),
        }
    )

    email = forms.EmailField(
        label=_("Email"),
        required=True,
        help_text=_("Obligatoriu. Folosiți un email valid."),
        error_messages={
            'required': _("Acest câmp este obligatoriu."),
        }
    )

    password1 = forms.CharField(
        label=_("Parolă"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_(
            "• Nu este recomandabil ca parola să fie asemănătoare cu celelalte date personale.<br>"
            "• Parola trebuie să conțină cel puțin 8 caractere.<br>"
            "• Parola nu poate fi atât de comună.<br>"
            "• Parola nu poate fi doar cu numere."
        ),
        error_messages={
            'required': _("Acest câmp este obligatoriu."),
        }
    )

    password2 = forms.CharField(
        label=_("Confirmare parolă"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_("Introduceți parola precedentă pentru confirmare."),
        error_messages={
            'required': _("Acest câmp este obligatoriu."),
        }
    )

    first_name = forms.CharField(
        label=_("Prenume"),
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Bob'})
    )

    last_name = forms.CharField(
        label=_("Nume"),
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'the builder'})
    )

    is_staff = forms.BooleanField(
        label=_("Status autorizare"),
        required=False,
        initial=False,
        help_text=_("Determină dacă acest utilizator se poate autentifica în acest site de administrare.")
    )

    is_superuser = forms.BooleanField(
        label=_("Status superutilizator"),
        required=False,
        initial=False,
        help_text=_(
            "Determină dacă acest utilizator are toate permisiunile, fără a fi nevoie să le selectați explicit.")
    )

    is_active = forms.BooleanField(
        label=_("Activ"),
        required=False,
        initial=True,
        help_text=_(
            "Determină dacă acest utilizator trebuie tratat ca activ. Dezactivați această opțiune în loc să ștergeți contul.")
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',
                  'first_name', 'last_name',
                  'is_staff', 'is_superuser', 'is_active')

    def clean(self):
        """✅ SOLUȚIA CHEIE: Setează automat permisiunile pentru instructori"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if email and email.endswith('@instructor.com'):
            cleaned_data['is_staff'] = True
            cleaned_data['is_superuser'] = False

            self.fields['is_staff'].widget.attrs['readonly'] = True
            self.fields['is_superuser'].widget.attrs['readonly'] = True

            self.fields['is_staff'].help_text += " <strong>(setat automat pentru instructori)</strong>"

        if cleaned_data.get('is_superuser', False):
            cleaned_data['is_staff'] = True

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        if user.email and user.email.endswith('@instructor.com'):
            user.is_staff = True
            user.is_superuser = False

        if commit:
            user.save()

        return user


class AdminUserChangeForm(UserChangeForm):
    """Formular pentru modificarea utilizatorilor în admin"""

    password1 = forms.CharField(
        label=_("Parolă nouă"),
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': 'Lăsați gol pentru a păstra parola actuală'
        }),
        strip=False,
        required=False,
        help_text=_("Lăsați gol pentru a păstra parola existentă."),
    )

    password2 = forms.CharField(
        label=_("Confirmare parolă nouă"),
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': 'Introduceți aceeași parolă'
        }),
        strip=False,
        required=False,
        help_text=_("Introduceți aceeași parolă pentru confirmare."),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'is_staff', 'is_superuser', 'is_active',
                  'groups', 'user_permissions',
                  'last_login', 'date_joined')

        labels = {
            'is_staff': _('Status autorizare'),
            'is_superuser': _('Status superutilizator'),
            'is_active': _('Activ'),
        }

        help_texts = {
            'is_staff': _("Determină dacă acest utilizator se poate autentifica în acest site de administrare."),
            'is_superuser': _(
                "Determină dacă acest utilizator are toate permisiunile, fără a fi nevoie să le selectați explicit."),
            'is_active': _(
                "Determină dacă acest utilizator trebuie tratat ca activ. Dezactivați această opțiune în loc să ștergeți contul."),
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if email and email.endswith('@instructor.com'):
            cleaned_data['is_staff'] = True
            cleaned_data['is_superuser'] = False

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)

        if user.email and user.email.endswith('@instructor.com'):
            user.is_staff = True
            user.is_superuser = False

        if commit:
            user.save()
            self.save_m2m()

        return user


# ============================================
# 2. FORMULARE PENTRU QUIZ
# ============================================

class QuizForm(forms.Form):
    """Formular pentru quiz-uri"""

    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super(QuizForm, self).__init__(*args, **kwargs)

        for question in questions:
            self.fields[f'question_{question.id}'] = forms.ModelChoiceField(
                queryset=question.answers.all(),
                widget=forms.RadioSelect,
                label=question.text,
                required=True
            )