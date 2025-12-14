from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.views.generic import TemplateView

from .models import (
    CustomUser, Client, Produit, Stock,
    Commande, DetailCommande, Paiement, Alerte, Culture, MouvementFinance
)

User = get_user_model()


# --- Vue personnalisée pour la liste d'utilisateurs ---
class UserListView(TemplateView):
    template_name = 'admin/liste_utilisateurs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        return context


# --- AdminSite personnalisé ---
class MyAdminSite(admin.AdminSite):
    site_header = "Admin Personnalisé"
    site_title = "Gestion Agricole"
    index_title = "Bienvenue sur l’admin personnalisé"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('utilisateurs/', self.admin_view(UserListView.as_view()), name='utilisateurs'),
        ]
        return custom_urls + urls


# --- Inlines ---
class DetailInline(admin.TabularInline):
    model = DetailCommande
    extra = 0
    readonly_fields = ('prix_unitaire',)


# --- Modèles enregistrés ---
@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'date_commande', 'statut', 'total')
    list_filter = ('statut',)
    search_fields = ('client__username',)
    inlines = [DetailInline]


@admin.register(DetailCommande)
class DetailCommandeAdmin(admin.ModelAdmin):
    list_display = ('commande', 'produit', 'quantite', 'prix_unitaire')

    @admin.action(description="Valider les commandes sélectionnées")
    def valider_commandes(self, request, queryset):
        updated = queryset.update(statut='confirmee')
        self.message_user(request, f"{updated} commande(s) validée(s).")

    @admin.action(description="Annuler les commandes sélectionnées")
    def annuler_commandes(self, request, queryset):
        updated = queryset.update(statut='annulee')
        self.message_user(request, f"{updated} commande(s) annulée(s).")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'admin', 'phone_number', 'created_at')
    search_fields = ('nom', 'admin__username', 'phone_number')


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = (
        'nom_produit',
        'stock_total',
        'prix_unitaire',
        'seuil_alerte',
        'image_preview',
    )
    search_fields = ('nom_produit',)
    list_editable = ('prix_unitaire', 'seuil_alerte')  # ⚠️ seulement les champs réels du modèle
    fieldsets = (
        (None, {
            'fields': (
                'nom_produit',
                'type_produit',
                'quantite',
                'prix_unitaire',
                'montant_total',
                'seuil_alerte',
                'image',
            )
        }),
    )

    @admin.display(description="Stock total")
    def stock_total(self, obj):
        total = Stock.objects.filter(produit=obj).aggregate(
            models.Sum('quantite')
        )['quantite__sum'] or 0
        return total

    @admin.display(description="Aperçu image")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;max-width:60px;object-fit:cover;border-radius:6px;" />',
                obj.image.url
            )
        return "Pas d’image"


# --- Instancier le site admin personnalisé et enregistrer les modèles ---
my_admin_site = MyAdminSite(name='myadmin')
my_admin_site.register(User, UserAdmin)
my_admin_site.register(Client, ClientAdmin)
my_admin_site.register(Produit, ProduitAdmin)
my_admin_site.register(Commande, CommandeAdmin)
my_admin_site.register(DetailCommande, DetailCommandeAdmin)
my_admin_site.register(Alerte)
my_admin_site.register(Stock)
my_admin_site.register(Paiement)
my_admin_site.register(Culture)
my_admin_site.register(MouvementFinance)
