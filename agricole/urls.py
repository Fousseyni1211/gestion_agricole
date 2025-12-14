from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

# Import views using absolute imports
from agricole import views
from agricole.views import contact_view, services_view, connexion_view, liste_clients, activer_client, desactiver_client

# Import view modules
from agricole import ClientViews, AgriculteurViews, AdminViews, agriculteur_management, AdminViews_agricole, AgronomeViews

# Import specific views from AgriculteurViews
from agricole.AgriculteurViews import (
    export_excel_mouvements,
    ajouter_mouvement,
    mouvements_recap,
    export_resume_pdf,
    export_pdf_mouvements
)
from .notifications_views import (mark_notification_as_read, mark_all_notifications_as_read,
                               delete_notification, get_notifications, notification_list,
                               delete_all_notifications, create_test_notification)

# Import de la vue de débogage
from .debug_views import debug_agriculteurs

# Import des vues financières
from . import financial_views

# Import des vues de stock améliorées (test version)
from . import stock_views_test as stock_views
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('contact', views.contact, name="contact"),
    path('login', views.loginUser, name="login"),
    path('logout_user', views.logout_user, name="logout_user"),
    path('registration', views.registration, name="registration"),
    path('doLogin', views.doLogin, name="doLogin"),
    path('doRegistration', views.doRegistration, name="doRegistration"),

    # URL for Admin
    # path('admin/utilisateurs/', AdminViews.liste_utilisateurs, name='admin_utilisateurs'),
    path('gerant_home/', AdminViews.admin_home, name="gerant_home"),
    path('gerant/materiels-agricoles/', AdminViews.materiels_agricoles, name="gerant_materiels_agricoles"),
    
    # Equipment Rental Management URLs
    path('gerant/materiels/ajouter/', AdminViews.ajouter_materiel, name="gerant_ajouter_materiel"),
    path('gerant/materiels/<int:materiel_id>/modifier/', AdminViews.modifier_materiel, name="gerant_modifier_materiel"),
    path('gerant/materiels/<int:materiel_id>/disponibilite/', AdminViews.gerer_disponibilite_materiel, name="gerant_disponibilite_materiel"),
    path('gerant/materiels/<int:materiel_id>/prix/', AdminViews.gerer_prix_materiel, name="gerant_prix_materiel"),
    path('gerant/reservations/', AdminViews.liste_reservations_materiel, name="gerant_reservations_materiel"),
    path('gerant/reservations/<int:reservation_id>/valider/', AdminViews.valider_reservation_materiel, name="gerant_valider_reservation_materiel"),
    path('gerant/reservations/<int:reservation_id>/annuler/', AdminViews.annuler_reservation_materiel, name="gerant_annuler_reservation_materiel"),
    path('gerant/planning-locations/', AdminViews.planning_locations, name="gerant_planning_locations"),
    path('gerant/statistiques-locations/', AdminViews.statistiques_locations, name="gerant_statistiques_locations"),
    
    path('rapports/', AdminViews.admin_reports, name='gerant_reports'),
    path('parametres/', AdminViews.admin_settings, name='gerant_settings'),
    path('add_produit/', AdminViews.add_produit, name="add_produit"),
    path('manage_produit/', AdminViews.manage_produit, name='manage_produit'),
    path('gerant_profile/', AdminViews.admin_profile, name='gerant_profile'),
    path('edit_product/<produit_id>/', AdminViews.edit_product, name="edit_product"),
    path('delete_product/<int:produit_id>/', AdminViews.delete_product, name='delete_product'),
    path('delete_product_confirm/<int:produit_id>/', AdminViews.delete_product_confirm, name='delete_product_confirm'),
    # path('admin_home/', AdminViews.admin_dashboard, name='admin_dashboard'),

    # URL pour gérer les utilisateurs
    path('manage_users/', AdminViews.manage_users, name='manage_users'),
    # URL pour ajouter un utilisateur
    path('add_user/', AdminViews.add_user, name='add_user'),
    # URL pour éditer un utilisateur
    path('edit_user/<int:id>/', AdminViews.edit_user, name='edit_user'),
    # URL pour supprimer un utilisateur
    path('delete_user/<int:id>/', AdminViews.delete_user, name='delete_user'),
    
    # URLs pour les notifications
    path('notifications/', notification_list, name='notification_list'),
    path('notifications/mark-as-read/<int:notification_id>/', mark_notification_as_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', mark_all_notifications_as_read, name='mark_all_notifications_read'),
    path('notifications/delete/<int:notification_id>/', delete_notification, name='delete_notification'),
    path('notifications/delete-all/', delete_all_notifications, name='delete_all_notifications'),
    path('notifications/test/', create_test_notification, name='create_test_notification'),
    path('api/notifications/', get_notifications, name='get_notifications'),

    path('services/', services_view, name='services'),
    # path('clients/ajouter/', AdminViews.ajouter_client, name='ajouter_client'),

    path("gerant/utilisateurs/", AdminViews.liste_utilisateurs, name="liste_utilisateurs"),
    path("gerant/utilisateur/<int:user_id>/activer/", AdminViews.activer_utilisateur, name="activer_utilisateur"),
    path("gerant/utilisateur/<int:user_id>/supprimer/", AdminViews.supprimer_utilisateur, name="supprimer_utilisateur"),
    path('ajouter_utilisateur/', AdminViews.ajouter_utilisateur, name="ajouter_utilisateur"),
    path('gerant/utilisateur/<int:user_id>/modifier/', AdminViews.modifier_utilisateur, name='modifier_utilisateur'),
    path('activer/<uidb64>/<token>/', AdminViews.activer_compte, name='activer_compte'),
    # path('orders/', AdminViews.order_list, name='order_list'),
    # path('orders/create/', AdminViews.create_order, name='create_order'),
    # path('orders/<int:order_id>/update-status/', AdminViews.update_order_status, name='update_order_status'),
    path('manage_payments/', views.manage_payments, name='manage_payments'),
    path('commandes/en_attente/', AdminViews.commandes_en_attente, name='commandes_en_attente'),
    path('stock_movement/', AdminViews.stock_movement, name='stock_movement'),
    path('weather/', views.weather_forecast, name='weather_forecast'),
    path('meteo/', views.weather_forecast, name='weather_forecast'),
    # path('login', views.login, name='login'),
    path('', views.landing_page, name='landing_page'),
    path('contact/', contact_view, name='contact'),
    path('stock/', AdminViews.liste_stock, name='liste_stock'),
    path('stock/ajouter/', AdminViews.ajouter_mouvement, name='ajouter_mouvements'),
    path('stock/exporter_excel/', AdminViews.exporter_stock_excel, name='exporter_stock_excel'),
    path('stock/exporter_pdf/', AdminViews.exporter_stock_pdf, name='exporter_stock_pdf'),
    # path('login/', CustomLoginView.as_view(), name='login'),
    path('clients/', views.liste_clients, name='liste_clients'),
    path('clients/ajouter/', AdminViews.ajouter_client, name='ajouter_client'),
    path('clients/toggle/<int:client_id>/', AdminViews.toggle_activation_client, name='toggle_activation_client'),
    path('clients/<int:client_id>/activer/', activer_client, name='activer_client'),
    path('clients/<int:client_id>/desactiver/', desactiver_client, name='desactiver_client'),
    # URL 'clients/ajouter/' déjà défini à la ligne 76
    # commandes
    path('commandes/', AdminViews.liste_commandes, name='liste_commandes'),
    path('commandes/ajouter/', AdminViews.ajouter_commande, name='ajouter_commande'),
    path('commandes/modifier/<int:commande_id>/', AdminViews.modifier_commande, name='modifier_commande'),
    path('commandes/export/pdf/', AdminViews.export_commandes_pdf, name='export_commandes_pdf'),
    path('commandes/export/excel/', AdminViews.export_commandes_excel, name='export_commandes_excel'),
    path('paiements/initier/', AdminViews.initiate_payment, name='initiate_payment'),
    path('paiements/page-paiement/', AdminViews.page_paiement, name='page_paiement'),
    path('paiements/confirmer-espèces/<int:commande_id>/', AdminViews.confirm_cash_payment, name='confirm_cash_payment'),
    
    # Nouvelle URL pour la liste des paiements par client
    path('gerant/paiements/', AdminViews.liste_paiements_client, name='liste_paiements_client'),
    path('gerant/paiements/<int:paiement_id>/', AdminViews.detail_paiement, name='detail_paiement'),
    
    path('commander/', views.passer_commande, name='passer_commande'),
    path('commande/<int:pk>/', views.detail_commande, name='detail_commande'),
    path('facture/<int:pk>/', views.facture_pdf, name='facture_pdf'),
    # Restauration de l'URL pour generer_facture_pdf
    path('facture/<int:commande_id>/', views.generer_facture_pdf, name='generer_facture_pdf'),
    
    path('agriculteurs/', views.liste_agriculteurs, name='liste_agriculteurs'),
    path('ajouter-agriculteur/', AdminViews.ajouter_agriculteur, name='ajouter_agriculteur'),
    path('modifier-agriculteur/<int:pk>/', AdminViews.modifier_agriculteur, name='modifier_agriculteur'),
    path('supprimer-agriculteur/<int:pk>/', AdminViews.supprimer_agriculteur, name='supprimer_agriculteur'),

    # Agriculteurs
    path('agriculteurs/activer/<int:user_id>/', views.activer_agriculteur, name='activer_agriculteur'),
    path('agriculteurs/desactiver/<int:user_id>/', views.desactiver_agriculteur, name='desactiver_agriculteur'),
    path('agriculteurs/reset-password/<int:user_id>/', agriculteur_management.reset_password_agriculteur, name='reset_password_agriculteur'),
    path('agriculteurs/activity/<int:user_id>/', agriculteur_management.get_agriculteur_activity, name='get_agriculteur_activity'),
    path('agriculteurs/permissions/<int:user_id>/', agriculteur_management.manage_agriculteur_permissions, name='manage_agriculteur_permissions'),


    # Agriculteur
    path('agri_home/', AgriculteurViews.agri_home, name='agri_home'),
    path('cultures/', AgriculteurViews.liste_cultures, name='liste_cultures'),
    path('cultures/ajouter/', AgriculteurViews.ajouter_culture, name='ajouter_culture'),
    path('transactions/', AgriculteurViews.liste_transactions, name='liste_transaction'),
    path('transactions/ajouter/', AgriculteurViews.ajouter_transaction, name='ajouter'),
    path('culture/<int:culture_id>/', AgriculteurViews.detail_culture, name='detail_culture'),
    path('agriculteur/modifier/', AgriculteurViews.profil_modifier, name='profil_modifier'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('connexion/', connexion_view, name='login'),  # ta vue login
    path('finances/', AgriculteurViews.liste_finances, name='liste_finances'),
    path('finances/ajouter/', AgriculteurViews.ajouter_mouvement, name='ajouter_mouvement'),
    path('finances/pdf/', export_pdf_mouvements, name='export_pdf_mouvements'),
    path('finances/excel/', export_excel_mouvements, name='export_excel_mouvements'),
    path('finances/', mouvements_recap, name='mouvements_recap'),
    path('finances/export_resume_pdf/', export_resume_pdf, name='export_resume_pdf'),
    path('contact/', views.contact_view, name='contact'),
    path('location/', views.location_materiel, name='location_materiel'),
    path('gerant/reservations/', views.gestion_reservations, name='gestion_reservations'),
    path('gerant/reservations/valider/<int:reservation_id>/', views.valider_reservation, name='valider_reservation'),
    path('gerant/reservations/annuler/<int:reservation_id>/', views.annuler_reservation, name='annuler_reservation'),
    path('boutique/', AgriculteurViews.boutique_bio, name='boutique_bio'),
    # client
    # path('commandes/', views.mes_commandes, name='mes_commandes'),
    # path('commandes/nouvelle/', views.passer_commande, name='passer_commande'),
    path('client_home/', ClientViews.client_home, name='client_home'),
    path('client/parametres/', ClientViews.parametres_client, name='parametres_client'),
    path('client/commandes/', ClientViews.mes_commandes, name='mes_commandes'),
    path('client/paiements/', ClientViews.historique_paiements, name='historique_paiements'),
    path('client/factures/', ClientViews.factures_client, name='factures_client'),
    path('client/reservations/', ClientViews.mes_reservations, name='mes_reservations'),
    path('client/alertes/', ClientViews.mes_alertes, name='mes_alertes'),
    path('client/finance/', ClientViews.finance_client, name='finance_client'),
    path('client/cultures/', ClientViews.culture_client, name='culture_client'),
    path('client/boutique/', ClientViews.boutique_bio, name='boutique_bio'),
    path('client/conseil-agricole/', ClientViews.conseil_agricole, name='conseil_agricole'),
    path('client/finances/', ClientViews.recap_financier_client, name='recap_financier_client'),
    path('meteo/', ClientViews.meteo_client, name='meteo_client'),
    path('avis-client/', ClientViews.avis_client, name='avis_client'),
    path('client/profil/', ClientViews.profil_client, name='profil_client'),
    path('client/parametres/', ClientViews.parametres_client, name='parametres_client'),
    path('ajouter-commande/', ClientViews.passer_commande, name='passer_commande'),
    path('mes-commandes/', ClientViews.mes_commandes, name='mes_commandes'),
    path('client/commande/<int:commande_id>/', ClientViews.detail_commande, name='detail_commande'),
    path('commande/<int:commande_id>/supprimer/', ClientViews.supprimer_commande, name='supprimer_commande'),
    path('commande/<int:commande_id>/pdf/', ClientViews.export_pdf_commande, name='pdf_commande'),
    path('api/commande/<int:commande_id>/', ClientViews.api_detail_commande, name='api_detail_commande'),
    # path('commandes/export/excel/', ClientViews.export_excel_commandes, name='export_excel_commandes'),
    
    path('client/commande/nouvelle/', views.passer_commande, name='passer_commande'),
    path('client/commandes/', views.client_commandes, name='client_commandes'),
    path('gerant/commandes/', views.admin_liste_commandes, name='gerant_commandes'),
    path('gerant/commandes/<int:commande_id>/valider/', views.admin_valider_commande, name='gerant_valider_commande'),
    path('gerant/commandes/<int:commande_id>/update_status/', views.admin_update_order_status, name='gerant_update_order_status'),
    path('gerant/commandes/<int:commande_id>/supprimer/', views.admin_supprimer_commande, name='gerant_supprimer_commande'),
    path('gerant/commandes/<int:commande_id>/annuler/', views.admin_annuler_commande, name='gerant_annuler_commande'),
    path('commandes/<int:commande_id>/export_pdf/', views.export_commande_pdf, name='export_commande_pdf'),

    # Payment management for manager
    path('gerant/paiements/', views.gerant_liste_paiements, name='gerant_paiements'),
    path('gerant/paiements/<int:paiement_id>/valider/', views.gerant_valider_paiement, name='gerant_valider_paiement'),
    path('gerant/paiements/<int:paiement_id>/rejeter/', views.gerant_rejeter_paiement, name='gerant_rejeter_paiement'),
    
    # Dashboard
    path('gerant/tableau-de-bord/', views.gerant_tableau_de_bord, name='gerant_tableau_de_bord'),

    
    # Notifications pour les administrateurs (utiliser admin_app au lieu de admin pour éviter les conflits)
    path('gerant_app/notifications/', views.admin_notifications, name='gerant_notifications'),
    path('gerant_app/notifications/<int:notification_id>/lue/', views.marquer_notification_lue, name='marquer_notification_lue'),
    
    # Notifications pour les clients
    path('client/notifications/', ClientViews.client_notifications, name='client_notifications'),
    path('client/notifications/<int:notification_id>/lue/', ClientViews.marquer_notification_lue, name='client_marquer_notification_lue'),
    
    # URLs pour les services
    path('demande-service/', views.demande_service, name='demande_service'),
    path('mes-demandes-service/', views.mes_demandes_service, name='mes_demandes_service'),
    path('gerant/demandes-service/', views.admin_liste_demandes_service, name='gerant_liste_demandes_service'),
    path('gerant/demandes-service/<int:demande_id>/', views.admin_detail_demande_service, name='gerant_detail_demande_service'),

    path('mes-demandes-service/', views.mes_demandes_service, name='mes_demandes_service'),
    path('gerant/demandes-service/', views.admin_liste_demandes_service, name='gerant_liste_demandes_service'),
    path('gerant/demandes-service/<int:demande_id>/', views.admin_detail_demande_service, name='gerant_detail_demande_service'),

    path('paiement/webhook/', views.payment_webhook, name='payment_webhook'),
    
    # URL pour la page de paiement
    path('paiement/commande/<int:commande_id>/', views.pay_for_order, name='paiement'),
    path('paiement/confirmation/<int:commande_id>/', views.confirmation_paiement, name='confirmation_paiement'),
    
    # URL de débogage pour les agriculteurs
    path('debug/agriculteurs/', debug_agriculteurs, name='debug_agriculteurs'),

    # ==================== GESTION AGRICOLE ====================
    # Tableau de bord agricole
    path('gerant/agricole/', AdminViews_agricole.tableau_de_bord_agricole, name='tableau_de_bord_agricole'),
    
    # Gestion des cultures
    path('gerant/cultures/', AdminViews_agricole.liste_cultures, name='liste_cultures'),
    path('gerant/cultures/ajouter/', AdminViews_agricole.ajouter_culture, name='ajouter_culture'),
    path('gerant/cultures/modifier/<int:culture_id>/', AdminViews_agricole.modifier_culture, name='modifier_culture'),
    path('gerant/cultures/supprimer/<int:culture_id>/', AdminViews_agricole.supprimer_culture, name='supprimer_culture'),
    
    # Gestion des parcelles
    path('gerant/parcelles/', AdminViews_agricole.liste_parcelles, name='liste_parcelles'),
    path('gerant/parcelles/ajouter/', AdminViews_agricole.ajouter_parcelle, name='ajouter_parcelle'),
    path('gerant/parcelles/modifier/<int:parcelle_id>/', AdminViews_agricole.modifier_parcelle, name='modifier_parcelle'),
    path('gerant/parcelles/assigner/<int:parcelle_id>/', AdminViews_agricole.assigner_parcelle, name='assigner_parcelle'),
    path('gerant/parcelles/supprimer/<int:parcelle_id>/', AdminViews_agricole.supprimer_parcelle, name='supprimer_parcelle'),
    
    # Gestion des itinéraires techniques
    path('gerant/itineraires/', AdminViews_agricole.liste_itineraires_techniques, name='liste_itineraires_techniques'),
    path('gerant/itineraires/ajouter/', AdminViews_agricole.ajouter_itineraire_technique, name='ajouter_itineraire_technique'),
    path('gerant/itineraires/modifier/<int:itineraire_id>/', AdminViews_agricole.modifier_itineraire_technique, name='modifier_itineraire_technique'),
    
    # Validation des activités agricoles
    path('gerant/activites/', AdminViews_agricole.liste_activites_agricoles, name='liste_activites_agricoles'),
    path('gerant/activites/valider/<int:activite_id>/', AdminViews_agricole.valider_activite_agricole, name='valider_activite_agricole'),
    
    # ==================== TECHNICIEN AGRONOME ====================
    
    # Tableau de bord et actions rapides
    path('agronome/', AgronomeViews.tableau_de_bord_agronome, name='tableau_de_bord_agronome'),
    
    # Validation des actions agricoles
    path('agronome/validation/arrosages/', AgronomeViews.validation_arrosages, name='validation_arrosages'),
    path('agronome/validation/traitements/', AgronomeViews.validation_traitements, name='validation_traitements'),
    path('agronome/validation/fertilisations/', AgronomeViews.validation_fertilisations, name='validation_fertilisations'),
    path('agronome/validation/valider/<int:activite_id>/', AgronomeViews.valider_action, name='valider_action'),
    path('agronome/validation/refuser/<int:activite_id>/', AgronomeViews.refuser_action, name='refuser_action'),
    
    # Vérification des photos
    path('agronome/photos/', AgronomeViews.verification_photos, name='verification_photos'),
    path('agronome/photos/valider/<int:photo_id>/', AgronomeViews.valider_photo, name='valider_photo'),
    
    # Suivi santé des cultures
    path('agronome/suivi-sante/', AgronomeViews.suivi_sante_cultures, name='suivi_sante_cultures'),
    
    # Fiches-conseils
    path('agronome/fiches-conseils/', AgronomeViews.liste_fiches_conseils, name='liste_fiches_conseils'),
    path('agronome/fiches-conseils/creer/', AgronomeViews.creer_fiche_conseil, name='creer_fiche_conseil'),
    path('agronome/fiches-conseils/modifier/<int:fiche_id>/', AgronomeViews.modifier_fiche_conseil, name='modifier_fiche_conseil'),
    
    # ==================== GESTION FINANCIÈRE ====================
    
    # Tableau de bord financier
    path('gerant/finances/', financial_views.tableau_bord_financier, name='tableau_bord_financier'),
    
    # Gestion des dépenses
    path('gerant/finances/depenses/', financial_views.liste_depenses, name='liste_depenses'),
    path('gerant/finances/depenses/ajouter/', financial_views.ajouter_depense, name='ajouter_depense'),
    path('gerant/finances/depenses/modifier/<int:pk>/', financial_views.modifier_depense, name='modifier_depense'),
    path('gerant/finances/depenses/supprimer/<int:pk>/', financial_views.supprimer_depense, name='supprimer_depense'),
    
    # Gestion des revenus
    path('gerant/finances/revenus/', financial_views.liste_revenus, name='liste_revenus'),
    path('gerant/finances/revenus/ajouter/', financial_views.ajouter_revenu, name='ajouter_revenu'),
    path('gerant/finances/revenus/modifier/<int:pk>/', financial_views.modifier_revenu, name='modifier_revenu'),
    path('gerant/finances/revenus/supprimer/<int:pk>/', financial_views.supprimer_revenu, name='supprimer_revenu'),
    
    # Gestion des factures
    path('gerant/finances/factures/', financial_views.liste_factures, name='liste_factures'),
    path('gerant/finances/factures/ajouter/', financial_views.ajouter_facture, name='ajouter_facture'),
    path('gerant/finances/factures/<int:pk>/', financial_views.detail_facture, name='detail_facture'),
    
    # Gestion des paiements clients
    path('gerant/finances/factures/<int:facture_id>/paiement/', financial_views.ajouter_paiement_client, name='ajouter_paiement_client'),
    
    # Suivi des soldes mensuels
    path('gerant/finances/soldes/', financial_views.soldes_mensuels, name='soldes_mensuels'),
    path('gerant/finances/soldes/recalculer/', financial_views.recalculer_soldes, name='recalculer_soldes'),
    
    # Rapports financiers
    path('gerant/finances/rapports/', financial_views.liste_rapports_financiers, name='liste_rapports_financiers'),
    path('gerant/finances/rapports/generer/', financial_views.generer_rapport_financier, name='generer_rapport_financier'),
    
    # Gestion des catégories
    path('gerant/finances/categories-depenses/', financial_views.categories_depenses, name='categories_depenses'),
    path('gerant/finances/categories-revenus/', financial_views.categories_revenus, name='categories_revenus'),

    # ==================== GESTION DE STOCK AMÉLIORÉE ====================
    
    # Tableau de bord du stock
    path('gerant/stock/', stock_views.tableau_bord_stock, name='tableau_bord_stock'),
    
    # Gestion du stock
    path('gerant/stock/liste/', stock_views.liste_stock_ameliore, name='liste_stock_ameliore'),
    path('gerant/stock/ajouter-entree/', stock_views.ajouter_entree_stock, name='ajouter_entree_stock'),
    
    # Mouvements de stock
    path('gerant/stock/mouvements/', stock_views.mouvements_stock_ameliore, name='mouvements_stock_ameliore'),
    
    # Exportation
    path('gerant/stock/exporter-excel/', stock_views.exporter_stock_ameliore_excel, name='exporter_stock_ameliore_excel'),
    
    # Gestion des commandes avec stock
    path('gerant/commandes/<int:commande_id>/valider-stock/', stock_views.valider_commande_avec_stock, name='valider_commande_avec_stock'),
    path('gerant/commandes/<int:commande_id>/annuler-stock/', stock_views.annuler_commande_avec_stock, name='annuler_commande_avec_stock'),
    path('gerant/commandes/<int:commande_id>/details-stock/', stock_views.details_commande_stock, name='details_commande_stock'),
    
    # Vérification AJAX
    path('gerant/stock/verifier-disponibilite/', stock_views.verifier_disponibilite_ajax, name='verifier_disponibilite_ajax'),
]
