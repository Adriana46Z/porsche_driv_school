from django.contrib import admin


class InstructorFilterMixin:

    def _is_instructor(self, user):
        return (
                user.is_authenticated and
                user.email and
                user.email.endswith('@instructor.com') and
                user.is_staff and
                not user.is_superuser
        )

    def get_model_perms(self, request):
        perms = super().get_model_perms(request)

        if self._is_instructor(request.user):
            allowed_models = ['Course', 'Question', 'Answer']
            model_name = self.model.__name__

            if model_name not in allowed_models:
                return {}

        return perms

    def has_module_permission(self, request):
        if self._is_instructor(request.user):
            allowed_models = ['Course', 'Question', 'Answer']
            model_name = self.model.__name__

            return model_name in allowed_models

        return super().has_module_permission(request)

    def has_add_permission(self, request):
        if self._is_instructor(request.user):
            allowed_models = ['Course', 'Question', 'Answer']
            model_name = self.model.__name__
            return model_name in allowed_models
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if self._is_instructor(request.user):
            allowed_models = ['Course', 'Question', 'Answer']
            model_name = self.model.__name__
            return model_name in allowed_models
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if self._is_instructor(request.user):
            allowed_models = ['Course', 'Question', 'Answer']
            model_name = self.model.__name__
            return model_name in allowed_models
        return super().has_delete_permission(request, obj)

    def has_view_permission(self, request, obj=None):
        if self._is_instructor(request.user):
            allowed_models = ['Course', 'Question', 'Answer']
            model_name = self.model.__name__
            return model_name in allowed_models
        return super().has_view_permission(request, obj)