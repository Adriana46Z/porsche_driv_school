from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.contrib import messages
from django.shortcuts import redirect

from .models import Course, Meme, Question, Answer, QuizAttempt
from .admin_filters import InstructorFilterMixin
from .forms import AdminUserCreationForm, AdminUserChangeForm

try:
    admin.site.unregister(User)
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    max_num = 4
    can_delete = True

    fields = ['text', 'is_correct']

    verbose_name = "Răspuns"
    verbose_name_plural = "Răspunsuri"

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        formset.form.base_fields['text'].label = "Text răspuns"
        formset.form.base_fields['is_correct'].label = "Corect?"

        formset.form.base_fields['text'].widget.attrs['placeholder'] = 'Introduceți răspunsul...'

        return formset

    def _is_instructor(self, user):
        return (
                user.is_authenticated and
                user.email and
                user.email.endswith('@instructor.com') and
                user.is_staff and
                not user.is_superuser
        )

    def has_add_permission(self, request, obj=None):
        if self._is_instructor(request.user):
            return True
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if self._is_instructor(request.user):
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if self._is_instructor(request.user):
            return True
        return super().has_delete_permission(request, obj)

    def has_view_permission(self, request, obj=None):
        if self._is_instructor(request.user):
            return True
        return super().has_view_permission(request, obj)


@admin.register(Answer)
class AnswerAdmin(InstructorFilterMixin, admin.ModelAdmin):
    list_display = ['text', 'question', 'is_correct']
    list_filter = ['is_correct']
    search_fields = ['text', 'question__text']

    def has_module_permission(self, request):
        return False

@admin.register(Question)
class QuestionAdmin(InstructorFilterMixin, admin.ModelAdmin):
    inlines = [AnswerInline]

    list_display = ['text', 'category', 'points', 'get_answers_count']
    list_filter = ['category']
    search_fields = ['text']
    list_per_page = 20

    fieldsets = [
        ('Întrebare', {
            'fields': ['text', 'image'],
            'description': 'Introduceți textul întrebării'
        }),
        ('Setări', {
            'fields': ['category', 'points'],
            'description': 'Selectați categoria și punctajul'
        }),
    ]

    def get_answers_count(self, obj):
        return obj.answers.count()

    get_answers_count.short_description = 'Nr. răspunsuri'


@admin.register(Course)
class CourseAdmin(InstructorFilterMixin, admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'order', 'created_at', 'has_pdf']
    list_filter = ['difficulty']
    search_fields = ['title', 'content']
    list_per_page = 20

    fieldsets = [
        (None, {'fields': ['title', 'content']}),
        ('Fișiere', {'fields': ['image', 'pdf_file']}),
        ('Configurare', {'fields': ['difficulty', 'order']}),
    ]

    def has_pdf(self, obj):
        return bool(obj.pdf_file)

    has_pdf.boolean = True
    has_pdf.short_description = 'Are PDF'


@admin.register(Meme)
class MemeAdmin(InstructorFilterMixin, admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title']
    list_per_page = 20

    def has_module_permission(self, request):
        if self._is_instructor(request.user):
            return False
        return super().has_module_permission(request)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(InstructorFilterMixin, admin.ModelAdmin):
    list_display = ['user', 'score', 'total_questions', 'percentage', 'category', 'completed_at']
    list_filter = ['category', 'completed_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user', 'score', 'total_questions', 'category', 'completed_at']
    list_per_page = 20

    def percentage(self, obj):
        if obj.total_questions > 0:
            return f"{(obj.score / obj.total_questions * 100):.1f}%"
        return "0%"

    percentage.short_description = 'Procentaj'

    def has_module_permission(self, request):
        if self._is_instructor(request.user):
            return False
        return super().has_module_permission(request)


class CustomUserAdmin(UserAdmin):
    add_form = AdminUserCreationForm
    form = AdminUserChangeForm

    list_display = ['username', 'email', 'first_name', 'last_name',
                    'is_staff', 'is_superuser', 'date_joined', 'user_type']
    list_filter = ['is_staff', 'is_superuser', 'date_joined', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_per_page = 50
    ordering = ['-date_joined']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2',
                       'first_name', 'last_name'),
        }),
        ('Permisiuni', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informații personale', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisiuni', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        ('Date importante', {'fields': ('last_login', 'date_joined')}),
    )

    readonly_fields = ['last_login', 'date_joined']

    def user_type(self, obj):
        if obj.is_superuser:
            return format_html('<span style="color: #dc3545; font-weight: bold;">👑 Superuser</span>')
        elif obj.email and obj.email.endswith('@instructor.com'):
            return format_html('<span style="color: #28a745; font-weight: bold;">👨‍🏫 Instructor</span>')
        elif obj.is_staff:
            return format_html('<span style="color: #17a2b8;">👤 Staff</span>')
        else:
            return format_html('<span style="color: #6c757d;">👤 Normal</span>')

    user_type.short_description = 'Tip utilizator'

    def save_model(self, request, obj, form, change):
        if not change:
            if 'password1' in form.cleaned_data and form.cleaned_data['password1']:
                obj.set_password(form.cleaned_data['password1'])
            else:
                default_password = f"{obj.username}123"
                obj.set_password(default_password)
                messages.info(request, f"Parola setată automat la: {default_password}")

            if obj.email and obj.email.endswith('@instructor.com'):
                obj.is_staff = True
                obj.is_superuser = False
                messages.info(request, f"Utilizatorul {obj.email} a fost setat ca instructor.")

        elif change and 'password1' in form.cleaned_data and form.cleaned_data['password1']:
            obj.set_password(form.cleaned_data['password1'])
            messages.success(request, f"Parola pentru {obj.username} a fost actualizată.")

        super().save_model(request, obj, form, change)

    def get_model_perms(self, request):
        if not request.user.is_superuser:
            return {}
        return super().get_model_perms(request)

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser


class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    filter_horizontal = ['permissions']

    def get_model_perms(self, request):
        if not request.user.is_superuser:
            return {}
        return super().get_model_perms(request)

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser


admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, CustomGroupAdmin)


class PorscheAdminSite(admin.AdminSite):
    site_header = "🏎️ Porsche School Administration"
    site_title = "Porsche School Admin"
    index_title = "Panou de Administrare"

    def login(self, request, extra_context=None):
        extra_context = extra_context or {}

        if request.user.is_authenticated:
            if (request.user.email and
                    request.user.email.endswith('@instructor.com') and
                    request.user.is_staff and
                    not request.user.is_superuser):
                messages.info(
                    request,
                    f"👨‍🏫 Bine ai venit, instructor {request.user.first_name}! "
                    f"Ai acces la gestionarea cursurilor și întrebărilor."
                )

        return super().login(request, extra_context)

    def each_context(self, request):
        context = super().each_context(request)

        is_instructor = (
                request.user.is_authenticated and
                request.user.email and
                request.user.email.endswith('@instructor.com') and
                request.user.is_staff and
                not request.user.is_superuser
        )

        context.update({
            'is_instructor': is_instructor,
            'site_header': self.site_header,
        })

        return context


original_site = admin.site
admin.site = PorscheAdminSite(name='porsche_admin')

for model, model_admin in original_site._registry.items():
    admin.site.register(model, model_admin.__class__)


def check_all_users():
    from django.contrib.auth.models import User

    print("🔍 Verificare utilizatori existenți...")
    print("=" * 60)

    for user in User.objects.all():
        status = []

        if user.is_superuser:
            status.append("👑 SUPERUSER")
        if user.is_staff:
            status.append("👤 STAFF")
        if user.email and '@instructor.com' in user.email:
            status.append("👨‍🏫 INSTRUCTOR")

        status_str = " | ".join(status) if status else "👤 NORMAL"

        print(f"{user.username} ({user.email}):")
        print(f"  {status_str}")
        print(f"  is_staff: {user.is_staff}, is_superuser: {user.is_superuser}")
        print(f"  Active: {user.is_active}")

        if user.password and not user.password.startswith('!'):
            print(f"  🔐 Parola: SETATĂ CORECT")
        else:
            print(f"  ⚠️  Parola: POSIBILĂ PROBLEMĂ")

        print()