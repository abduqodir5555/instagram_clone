from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from users.models import User, CodeVerify


admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ("username", "email", "phone_number", "first_name", "last_name", "is_staff")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "phone_number", "photo")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "auth_type",
                    "auth_status",
                    "auth_role",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


class CodeverifyAdmin(admin.ModelAdmin):
    list_display = ('user', 'verify_type', 'is_confirmed')
    list_filter = ('verify_type', 'is_confirmed')
    search_fields = ('user__username', )


admin.site.register(CodeVerify, CodeverifyAdmin)
