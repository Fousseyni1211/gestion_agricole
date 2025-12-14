from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import render
from django.contrib.admin.views.main import ChangeList
from .models import CustomUser

class MyAdminSite(AdminSite):
    site_header = 'Administration Kayupe'
    site_title = 'Kayupe Admin'
    index_title = 'Bienvenue sur l’admin Kayupe'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('utilisateurs/', self.admin_view(self.user_changelist_view), name='utilisateurs'),
        ]
        return custom_urls + urls

    def user_changelist_view(self, request):
        UserModel = CustomUser
        cl = ChangeList(
            request, UserModel, [], [], [], [], [], [], [], [],
            admin_site=self
        )
        queryset = cl.get_queryset(request)
        context = dict(
            self.each_context(request),
            title='Liste des utilisateurs',
            cl=cl,
            queryset=queryset,
            opts=UserModel._meta,
            app_label=UserModel._meta.app_label,
            model_name=UserModel._meta.model_name,
        )
        return render(request, 'admin/customuser_changelist.html', context)

my_admin_site = MyAdminSite(name='myadmin')

# Enregistre le modèle CustomUser avec UserAdmin classique
my_admin_site.register(CustomUser, UserAdmin)
