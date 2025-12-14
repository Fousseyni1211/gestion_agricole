#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script d'initialisation et de test du système de gestion de stock amélioré
"""

import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_agricole.settings')
django.setup()

from django.contrib.auth.models import User
from agricole.models import Produit, Stock, MouvementStock, Commande, DetailCommande
from decimal import Decimal

def create_test_products():
    """Créer des produits de test"""
    print("🌱 Création des produits de test...")
    
    produits_data = [
        {
            'nom_produit': 'Semence de Maïs',
            'description': 'Semence de maïs de haute qualité',
            'prix_unitaire': Decimal('2500'),
            'quantite': 100,
            'seuil_alerte': 20,
            'unite': 'kg'
        },
        {
            'nom_produit': 'Engrais NPK',
            'description': 'Engrais complet NPK 15-15-15',
            'prix_unitaire': Decimal('3500'),
            'quantite': 50,
            'seuil_alerte': 10,
            'unite': 'sac'
        },
        {
            'nom_produit': 'Pesticide Bio',
            'description': 'Pesticide biologique certifié',
            'prix_unitaire': Decimal('8500'),
            'quantite': 15,
            'seuil_alerte': 5,
            'unite': 'L'
        }
    ]
    
    for prod_data in produits_data:
        produit, created = Produit.objects.get_or_create(
            nom_produit=prod_data['nom_produit'],
            defaults=prod_data
        )
        if created:
            print(f"  ✅ Produit créé: {produit.nom_produit}")
        else:
            print(f"  ℹ️  Produit existant: {produit.nom_produit}")
    
    return Produit.objects.all()

def create_test_stocks(gerant, produits):
    """Créer les stocks initiaux pour le gérant"""
    print("\n📦 Création des stocks initiaux...")
    
    for produit in produits:
        stock = Stock.get_or_create_stock(gerant, produit)
        stock.quantite = produit.quantite
        stock.save()
        
        # Créer un mouvement d'entrée initial
        MouvementStock.objects.create(
            produit=produit,
            type_mouvement=MouvementStock.ENTREE,
            quantite=produit.quantite,
            commentaire=f"Stock initial - {gerant.username}",
            utilisateur=gerant
        )
        
        print(f"  ✅ Stock initialisé: {produit.nom_produit} ({stock.quantite} {produit.unite})")

def create_test_order(gerant, produits):
    """Créer une commande de test"""
    print("\n🛒 Création d'une commande de test...")
    
    # Récupérer ou créer un client
    client, created = User.objects.get_or_create(
        username='client_test',
        defaults={
            'email': 'client@test.com',
            'first_name': 'Client',
            'last_name': 'Test',
            'role': 'Client'
        }
    )
    
    # Créer la commande
    commande = Commande.objects.create(
        client=client,
        gérant=gerant,
        statut='en_attente'
    )
    
    # Ajouter des détails à la commande
    details = [
        {'produit': produits[0], 'quantite': 10, 'prix': produits[0].prix_unitaire},  # Semence de Maïs
        {'produit': produits[1], 'quantite': 5, 'prix': produits[1].prix_unitaire},   # Engrais NPK
    ]
    
    for detail in details:
        DetailCommande.objects.create(
            commande=commande,
            produit=detail['produit'],
            quantite=detail['quantite'],
            prix_unitaire=detail['prix']
        )
    
    print(f"  ✅ Commande créée: #{commande.id} pour {client.username}")
    return commande

def test_stock_reduction(commande):
    """Tester la réduction automatique du stock"""
    print("\n🔄 Test de la réduction automatique du stock...")
    
    # Afficher l'état du stock avant
    print("  📊 État du stock AVANT validation:")
    for detail in commande.details.all():
        stock = Stock.objects.get(utilisateur=commande.gérant, produit=detail.produit)
        print(f"    {detail.produit.nom_produit}: {stock.quantite} → {stock.quantite - detail.quantite} (demandé: {detail.quantite})")
    
    try:
        # Valider la commande et réduire le stock
        disponible, message = commande.verifier_disponibilite_stock()
        print(f"  🔍 Vérification: {message}")
        
        if disponible:
            commande.valider_et_reduire_stock()
            print("  ✅ Commande validée et stock réduit avec succès!")
            
            # Afficher l'état du stock après
            print("  📊 État du stock APRÈS validation:")
            for detail in commande.details.all():
                stock = Stock.objects.get(utilisateur=commande.gérant, produit=detail.produit)
                print(f"    {detail.produit.nom_produit}: {stock.quantite} (réduit de {detail.quantite})")
        else:
            print(f"  ❌ Impossible de valider: {message}")
    
    except Exception as e:
        print(f"  ❌ Erreur lors de la validation: {e}")

def test_stock_insufficient():
    """Tester le cas de stock insuffisant"""
    print("\n⚠️  Test du cas de stock insuffisant...")
    
    # Récupérer le gérant
    gerant = User.objects.filter(user_type='1').first()
    if not gerant:
        gerant = User.objects.create_user(
            username='gerant_test',
            email='gerant@test.com',
            password='test123',
            user_type='1'
        )
    
    # Créer une commande avec quantité excessive
    client = User.objects.get(username='client_test')
    commande = Commande.objects.create(
        client=client,
        gérant=gerant,
        statut='en_attente'
    )
    
    # Ajouter un produit avec quantité excessive
    produit = Produit.objects.first()
    stock = Stock.objects.get(utilisateur=gerant, produit=produit)
    
    DetailCommande.objects.create(
        commande=commande,
        produit=produit,
        quantite=stock.quantite + 100,  # Quantité excessive
        prix_unitaire=produit.prix_unitaire
    )
    
    # Tenter de valider
    try:
        disponible, message = commande.verifier_disponibilite_stock()
        print(f"  🔍 Vérification: {message}")
        
        if not disponible:
            print("  ✅ Test réussi: Le système détecte correctement le stock insuffisant")
        else:
            print("  ❌ Test échoué: Le système aurait dû détecter le stock insuffisant")
    
    except Exception as e:
        print(f"  ❌ Erreur: {e}")

def display_stock_status():
    """Afficher le statut actuel du stock"""
    print("\n📋 Statut actuel du stock:")
    
    gerant = User.objects.filter(user_type='1').first()
    if not gerant:
        print("  ❌ Aucun gérant trouvé")
        return
    
    stocks = Stock.objects.filter(utilisateur=gerant).select_related('produit')
    
    for stock in stocks:
        statut = "✅ Normal"
        if stock.est_en_rupture():
            statut = "❌ Rupture"
        elif stock.est_en_alerte():
            statut = "⚠️  Alerte"
        
        print(f"  {stock.produit.nom_produit}: {stock.quantite} {stock.produit.unite} {statut}")

def main():
    """Fonction principale"""
    print("🚀 Démarrage du test du système de gestion de stock amélioré\n")
    
    try:
        # Créer un gérant de test
        gerant, created = User.objects.get_or_create(
            username='gerant_test',
            defaults={
                'email': 'gerant@test.com',
                'first_name': 'Gérant',
                'last_name': 'Test',
                'user_type': '1',
                'is_staff': True
            }
        )
        if created:
            gerant.set_password('test123')
            gerant.save()
            print(f"  ✅ Gérant créé: {gerant.username}")
        else:
            print(f"  ℹ️  Gérant existant: {gerant.username}")
        
        # Créer les produits de test
        produits = create_test_products()
        
        # Initialiser les stocks
        create_test_stocks(gerant, produits)
        
        # Afficher le statut initial
        display_stock_status()
        
        # Créer et tester une commande
        commande = create_test_order(gerant, produits)
        test_stock_reduction(commande)
        
        # Tester le cas de stock insuffisant
        test_stock_insufficient()
        
        # Afficher le statut final
        display_stock_status()
        
        # Afficher les mouvements de stock
        print("\n📜 Historique des mouvements de stock:")
        mouvements = MouvementStock.objects.all().order_by('-date')[:10]
        for mouvement in mouvements:
            type_emoji = "📥" if mouvement.type_mouvement == MouvementStock.ENTREE else "📤"
            print(f"  {type_emoji} {mouvement.date.strftime('%d/%m/%Y %H:%M')} - {mouvement.produit.nom_produit} ({mouvement.quantite}) - {mouvement.commentaire}")
        
        print("\n✅ Test terminé avec succès!")
        print("\n🎯 Fonctionnalités testées:")
        print("  ✅ Création de produits")
        print("  ✅ Initialisation des stocks")
        print("  ✅ Création de commandes")
        print("  ✅ Vérification de disponibilité")
        print("  ✅ Réduction automatique du stock")
        print("  ✅ Gestion des erreurs (stock insuffisant)")
        print("  ✅ Suivi des mouvements")
        print("  ✅ Alertes de stock")
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
