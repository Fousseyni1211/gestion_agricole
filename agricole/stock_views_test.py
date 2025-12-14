# -*- coding: utf-8 -*-
"""
Test simple pour vérifier si le problème vient du fichier stock_views.py
"""

def tableau_bord_stock(request):
    """Vue de test simple"""
    from django.http import HttpResponse
    return HttpResponse("Test: Stock dashboard is working!")

def liste_stock_ameliore(request):
    """Vue de test simple"""
    from django.http import HttpResponse
    return HttpResponse("Test: Stock list is working!")

def ajouter_entree_stock(request):
    """Vue de test simple"""
    from django.http import HttpResponse
    return HttpResponse("Test: Add stock entry is working!")

def mouvements_stock_ameliore(request):
    """Vue de test simple"""
    from django.http import HttpResponse
    return HttpResponse("Test: Stock movements is working!")

def exporter_stock_ameliore_excel(request):
    """Vue de test simple"""
    from django.http import HttpResponse
    return HttpResponse("Test: Export stock is working!")

def valider_commande_avec_stock(request, commande_id):
    """Vue de test simple"""
    from django.http import HttpResponse
    return HttpResponse(f"Test: Validate order {commande_id} is working!")

def annuler_commande_avec_stock(request, commande_id):
    """Vue de test simple"""
    from django.http import HttpResponse
    return HttpResponse(f"Test: Cancel order {commande_id} is working!")

def details_commande_stock(request, commande_id):
    """Vue de test simple"""
    from django.http import HttpResponse
    return HttpResponse(f"Test: Order details {commande_id} is working!")

def verifier_disponibilite_ajax(request):
    """Vue de test simple"""
    from django.http import JsonResponse
    return JsonResponse({"test": True, "message": "AJAX test is working!"})
