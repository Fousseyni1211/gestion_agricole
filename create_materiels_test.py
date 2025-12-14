#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_agricole.settings')
django.setup()

from agricole.models import Materiel

def create_test_materiels():
    """Créer des matériels de test pour la démo"""
    
    # Données de test pour les matériels
    materiels_data = [
        {
            'nom': 'Tracteur John Deere 5065E',
            'categorie': 'tracteurs',
            'description': 'Tracteur agricole puissant et fiable',
            'prix_location_jour': 50000,
            'marque': 'John Deere',
            'modele': '5065E',
            'quantite_totale': 2,
            'disponible': True
        },
        {
            'nom': 'Charrue 4 sillons',
            'categorie': 'outillage',
            'description': 'Charrue pour labour profond',
            'prix_location_jour': 15000,
            'marque': 'Kuhn',
            'modele': 'Multi-Master 153',
            'quantite_totale': 3,
            'disponible': True
        },
        {
            'nom': 'Moissonneuse-batteuse',
            'categorie': 'recolte',
            'description': 'Moissonneuse-batteuse performante',
            'prix_location_jour': 150000,
            'marque': 'Claas',
            'modele': 'Lexion 760',
            'quantite_totale': 1,
            'disponible': True
        },
        {
            'nom': 'Pulvérisateur agricole',
            'categorie': 'traitement',
            'description': 'Pulvérisateur pour traitements phytosanitaires',
            'prix_location_jour': 25000,
            'marque': 'Berthoud',
            'modele': 'Raptor',
            'quantite_totale': 2,
            'disponible': True
        },
        {
            'nom': 'Remorque agricole 5T',
            'categorie': 'transport',
            'description': 'Remorque robuste pour transport',
            'prix_location_jour': 20000,
            'marque': 'Bennes',
            'modele': 'AGRI-5000',
            'quantite_totale': 4,
            'disponible': True
        }
    ]
    
    print(f"Nombre de matériels avant: {Materiel.objects.count()}")
    
    # Créer les matériels
    for data in materiels_data:
        materiel = Materiel.objects.create(**data)
        materiel.quantite_disponible = materiel.quantite_totale
        materiel.save()
        print(f"Créé: {materiel.nom}")
    
    print(f"Nombre de matériels après: {Materiel.objects.count()}")

if __name__ == "__main__":
    create_test_materiels()
