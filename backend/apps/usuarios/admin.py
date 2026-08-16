from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Perfil", {"fields": ("tipo",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Perfil", {"fields": ("email", "tipo")}),)
    list_display = ("username", "email", "first_name", "last_name", "tipo", "is_staff")
