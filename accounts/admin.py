from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'prenom', 'nom', 'role', 'statut', 'is_staff')
    list_filter = ('role', 'statut', 'is_staff', 'is_superuser')
    search_fields = ('email', 'nom', 'prenom')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Identite', {'fields': ('nom', 'prenom', 'fonction')}),
        ('Roles et statut', {'fields': ('role', 'statut', 'niveau_acces')}),
        ('Permissions Django', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_inscription')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'nom',
                'prenom',
                'role',
                'password1',
                'password2',
                'is_staff',
                'is_superuser',
            ),
        }),
    )
    readonly_fields = ('last_login', 'date_inscription')
