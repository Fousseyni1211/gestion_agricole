#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_agricole.settings')
django.setup()

from agricole.models import CategorieDepense, CategorieRevenu
from django.contrib.auth import get_user_model

User = get_user_model()

def create_initial_categories():
    """Create initial financial categories"""
    
    # Categories de dépenses
    categories_depenses = [
        {'nom': 'Intrants', 'description': 'Semences, engrais, pesticides', 'couleur': '#28a745'},
        {'nom': 'Main d\'œuvre', 'description': 'Salaires et paiements journaliers', 'couleur': '#007bff'},
        {'nom': 'Carburant', 'description': 'Carburant pour tracteurs et machines', 'couleur': '#ffc107'},
        {'nom': 'Entretien matériel', 'description': 'Réparation et maintenance', 'couleur': '#17a2b8'},
        {'nom': 'Transport', 'description': 'Frais de transport et logistique', 'couleur': '#6f42c1'},
        {'nom': 'Services externes', 'description': 'Consultants et prestataires', 'couleur': '#e83e8c'},
        {'nom': 'Eau et irrigation', 'description': 'Coûts liés à l\'eau', 'couleur': '#20c997'},
        {'nom': 'Autres dépenses', 'description': 'Dépenses non classifiées', 'couleur': '#6c757d'},
    ]
    
    for cat_data in categories_depenses:
        categorie, created = CategorieDepense.objects.get_or_create(
            nom=cat_data['nom'],
            defaults=cat_data
        )
        if created:
            print(f"Catégorie de dépense créée: {categorie.nom}")
        else:
            print(f"Catégorie de dépense existe déjà: {categorie.nom}")
    
    # Categories de revenus
    categories_revenus = [
        {'nom': 'Vente produits', 'description': 'Vente de récoltes et produits agricoles', 'couleur': '#28a745'},
        {'nom': 'Location matériel', 'description': 'Location de matériel agricole', 'couleur': '#007bff'},
        {'nom': 'Services agricoles', 'description': 'Services fournis aux autres agriculteurs', 'couleur': '#ffc107'},
        {'nom': 'Subventions', 'description': 'Aides et subventions reçues', 'couleur': '#17a2b8'},
        {'nom': 'Vente bétail', 'description': 'Vente d\'animaux', 'couleur': '#6f42c1'},
        {'nom': 'Produits transformés', 'description': 'Vente de produits transformés', 'couleur': '#e83e8c'},
        {'nom': 'Autres revenus', 'description': 'Revenus non classifiés', 'couleur': '#6c757d'},
    ]
    
    for cat_data in categories_revenus:
        categorie, created = CategorieRevenu.objects.get_or_create(
            nom=cat_data['nom'],
            defaults=cat_data
        )
        if created:
            print(f"Catégorie de revenu créée: {categorie.nom}")
        else:
            print(f"Catégorie de revenu existe déjà: {categorie.nom}")

def create_test_data():
    """Create some test data for demonstration"""
    
    # Get admin user
    try:
        admin_user = User.objects.filter(user_type='1').first()  # Admin user
        if admin_user:
            print(f"Utilisateur admin trouvé: {admin_user.username}")
        else:
            raise User.DoesNotExist
    except (User.DoesNotExist, AttributeError):
        print("Aucun utilisateur admin trouvé. Création d'un utilisateur de test...")
        admin_user = User.objects.create_user(
            username='admin_finances',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='Finances',
            user_type='1'
        )
        print(f"Utilisateur admin créé: {admin_user.username}")
    
    # Create some test expenses
    from agricole.models import Depense, Revenu
    from datetime import date, timedelta
    
    # Test expenses
    test_expenses = [
        {
            'titre': 'Achat engrais NPK',
            'description': 'Engrais pour la saison de plantation',
            'montant': 150000,
            'date_depense': date.today() - timedelta(days=5),
            'fournisseur': 'Agro Supply',
            'numero_facture': 'FAC-2024-001',
            'categorie': CategorieDepense.objects.get(nom='Intrants')
        },
        {
            'titre': 'Carburant tracteur',
            'description': 'Diesel pour le tracteur John Deere',
            'montant': 75000,
            'date_depense': date.today() - timedelta(days=3),
            'fournisseur': 'Station Total',
            'numero_facture': 'FAC-2024-002',
            'categorie': CategorieDepense.objects.get(nom='Carburant')
        },
        {
            'titre': 'Salaires ouvriers',
            'description': 'Paie des ouvriers agricoles - semaine 1',
            'montant': 120000,
            'date_depense': date.today() - timedelta(days=2),
            'fournisseur': 'Salaires',
            'categorie': CategorieDepense.objects.get(nom='Main d\'œuvre')
        }
    ]
    
    for expense_data in test_expenses:
        expense, created = Depense.objects.get_or_create(
            titre=expense_data['titre'],
            utilisateur=admin_user,
            defaults=expense_data
        )
        if created:
            print(f"Dépense créée: {expense.titre} - {expense.montant} FCFA")
        else:
            print(f"Dépense existe déjà: {expense.titre}")
    
    # Test revenues
    test_revenus = [
        {
            'titre': 'Vente maïs',
            'description': 'Vente de la récolte de maïs - Lot A',
            'montant': 450000,
            'date_revenu': date.today() - timedelta(days=7),
            'client': 'Marché Central',
            'reference': 'VENTE-2024-001',
            'categorie': CategorieRevenu.objects.get(nom='Vente produits')
        },
        {
            'titre': 'Location moissonneuse',
            'description': 'Location de moissonneuse-batteuse à voisin',
            'montant': 80000,
            'date_revenu': date.today() - timedelta(days=4),
            'client': 'Agriculteur voisin',
            'reference': 'LOC-2024-001',
            'categorie': CategorieRevenu.objects.get(nom='Location matériel')
        }
    ]
    
    for revenu_data in test_revenus:
        revenu, created = Revenu.objects.get_or_create(
            titre=revenu_data['titre'],
            utilisateur=admin_user,
            defaults=revenu_data
        )
        if created:
            print(f"Revenu créé: {revenu.titre} - {revenu.montant} FCFA")
        else:
            print(f"Revenu existe déjà: {revenu.titre}")

if __name__ == '__main__':
    print("=== Initialisation des données financières ===")
    create_initial_categories()
    print("\n=== Création des données de test ===")
    create_test_data()
    print("\n=== Initialisation terminée ===")
    print("Vous pouvez maintenant accéder au tableau de bord financier:")
    print("1. Démarrez le serveur: python manage.py runserver")
    print("2. Connectez-vous en tant qu'administrateur")
    print("3. Accédez à: http://127.0.0.1:8000/gerant/finances/")
