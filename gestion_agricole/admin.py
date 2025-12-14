from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model

from .models import UtilisateurProxy

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    model = CustomUser

    list_display = ('username', 'first_name', 'last_name', 'email', 'afficher_role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    search_fields = ('username', 'email')
    ordering = ('username',)

    def afficher_role(self, obj):
        return obj.role
    afficher_role.short_description = 'Rôle'

class MyAdminSite(admin.AdminSite):
    site_header = "Admin de FAMA(Ferme Agricole pour la Meilleure Alimentation )"
    site_title = "Gestion Agricole"
    index_title = "Bienvenue sur l’admin Ferme Agricole pour la Meilleure Alimentation"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('utilisateurs/', self.admin_view(self.user_changelist), name='utilisateurs'),
        ]
        return custom_urls + urls

    def user_changelist(self, request):
        from django.urls import reverse
        from django.contrib.contenttypes.models import ContentType

        ct = ContentType.objects.get_for_model(UtilisateurProxy)
        url = reverse(f'{self.name}:{ct.app_label}_{ct.model}_changelist')
        return HttpResponseRedirect(url)

my_admin_site = MyAdminSite(name='myadmin')

# Enregistre le modèle proxy
my_admin_site.register(CustomUser, UserAdmin)
