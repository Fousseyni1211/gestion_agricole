# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Q, Count, Avg
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.paginator import Paginator
import json
from datetime import datetime, timedelta

from .models import (
    CategorieDepense, CategorieRevenu, Depense, Revenu, 
    SoldeMensuel, Facture, PaiementClient, RapportFinancier, Client
)
from .financial_forms import (
    CategorieDepenseForm, CategorieRevenuForm, DepenseForm, RevenuForm,
    FactureForm, PaiementClientForm, RapportFinancierForm,
    DepenseSearchForm, RevenuSearchForm, FactureSearchForm
)

# ====== VUES DE GESTION FINANCIÈRE ======

@login_required
def tableau_bord_financier(request):
    """Tableau de bord financier pour le gérant"""
    if request.user.user_type != '1':  # Admin seulement
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    # Statistiques du mois en cours
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    # Dépenses du mois
    depenses_mois = Depense.objects.filter(
        utilisateur=request.user,
        date_depense__month=current_month,
        date_depense__year=current_year,
        statut='validee'
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # Revenus du mois
    revenus_mois = Revenu.objects.filter(
        utilisateur=request.user,
        date_revenu__month=current_month,
        date_revenu__year=current_year,
        statut='validee'
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # Solde du mois
    solde_mois = revenus_mois - depenses_mois
    
    # Statistiques des factures
    factures_en_attente = Facture.objects.filter(statut='en_attente').count()
    factures_en_retard = Facture.objects.filter(statut='en_retard').count()
    
    # Dernières transactions
    dernieres_depenses = Depense.objects.filter(
        utilisateur=request.user,
        statut='validee'
    ).order_by('-date_depense')[:5]
    
    derniers_revenus = Revenu.objects.filter(
        utilisateur=request.user,
        statut='validee'
    ).order_by('-date_revenu')[:5]
    
    context = {
        'depenses_mois': depenses_mois,
        'revenus_mois': revenus_mois,
        'solde_mois': solde_mois,
        'factures_en_attente': factures_en_attente,
        'factures_en_retard': factures_en_retard,
        'dernieres_depenses': dernieres_depenses,
        'derniers_revenus': derniers_revenus,
        'current_month': current_month,
        'current_year': current_year,
    }
    
    return render(request, 'admin/finances/tableau_bord_financier.html', context)

# ====== GESTION DES DÉPENSES ======

@login_required
def liste_depenses(request):
    """Liste des dépenses avec filtres"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    depenses = Depense.objects.filter(utilisateur=request.user).order_by('-date_depense')
    
    # Formulaire de recherche
    search_form = DepenseSearchForm(request.GET)
    
    if search_form.is_valid():
        cleaned_data = search_form.cleaned_data
        
        if cleaned_data['categorie']:
            depenses = depenses.filter(categorie=cleaned_data['categorie'])
        
        if cleaned_data['date_debut']:
            depenses = depenses.filter(date_depense__gte=cleaned_data['date_debut'])
        
        if cleaned_data['date_fin']:
            depenses = depenses.filter(date_depense__lte=cleaned_data['date_fin'])
        
        if cleaned_data['statut']:
            depenses = depenses.filter(statut=cleaned_data['statut'])
    
    # Pagination
    paginator = Paginator(depenses, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_depenses': depenses.aggregate(total=Sum('montant'))['total'] or 0,
    }
    
    return render(request, 'admin/finances/liste_depenses.html', context)

@login_required
def ajouter_depense(request):
    """Ajouter une nouvelle dépense"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    if request.method == 'POST':
        form = DepenseForm(request.POST, request.FILES)
        if form.is_valid():
            depense = form.save(commit=False)
            depense.utilisateur = request.user
            depense.save()
            
            # Mettre à jour le solde mensuel
            solde_mensuel, created = SoldeMensuel.objects.get_or_create(
                utilisateur=request.user,
                annee=depense.date_depense.year,
                mois=depense.date_depense.month
            )
            solde_mensuel.calculer_solde()
            
            messages.success(request, "Dépense enregistrée avec succès")
            return redirect('liste_depenses')
    else:
        form = DepenseForm()
    
    return render(request, 'admin/finances/ajouter_depense.html', {'form': form})

@login_required
def modifier_depense(request, pk):
    """Modifier une dépense existante"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    depense = get_object_or_404(Depense, pk=pk, utilisateur=request.user)
    
    if request.method == 'POST':
        form = DepenseForm(request.POST, request.FILES, instance=depense)
        if form.is_valid():
            form.save()
            
            # Mettre à jour le solde mensuel
            solde_mensuel, created = SoldeMensuel.objects.get_or_create(
                utilisateur=request.user,
                annee=depense.date_depense.year,
                mois=depense.date_depense.month
            )
            solde_mensuel.calculer_solde()
            
            messages.success(request, "Dépense modifiée avec succès")
            return redirect('liste_depenses')
    else:
        form = DepenseForm(instance=depense)
    
    return render(request, 'admin/finances/modifier_depense.html', {'form': form, 'depense': depense})

@login_required
def supprimer_depense(request, pk):
    """Supprimer une dépense"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    depense = get_object_or_404(Depense, pk=pk, utilisateur=request.user)
    
    if request.method == 'POST':
        date_depense = depense.date_depense
        depense.delete()
        
        # Mettre à jour le solde mensuel
        solde_mensuel, created = SoldeMensuel.objects.get_or_create(
            utilisateur=request.user,
            annee=date_depense.year,
            mois=date_depense.month
        )
        solde_mensuel.calculer_solde()
        
        messages.success(request, "Dépense supprimée avec succès")
        return redirect('liste_depenses')
    
    return render(request, 'admin/finances/supprimer_depense.html', {'depense': depense})

# ====== GESTION DES REVENUS ======

@login_required
def liste_revenus(request):
    """Liste des revenus avec filtres"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    revenus = Revenu.objects.filter(utilisateur=request.user).order_by('-date_revenu')
    
    # Formulaire de recherche
    search_form = RevenuSearchForm(request.GET)
    
    if search_form.is_valid():
        cleaned_data = search_form.cleaned_data
        
        if cleaned_data['categorie']:
            revenus = revenus.filter(categorie=cleaned_data['categorie'])
        
        if cleaned_data['date_debut']:
            revenus = revenus.filter(date_revenu__gte=cleaned_data['date_debut'])
        
        if cleaned_data['date_fin']:
            revenus = revenus.filter(date_revenu__lte=cleaned_data['date_fin'])
        
        if cleaned_data['statut']:
            revenus = revenus.filter(statut=cleaned_data['statut'])
    
    # Pagination
    paginator = Paginator(revenus, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_revenus': revenus.aggregate(total=Sum('montant'))['total'] or 0,
    }
    
    return render(request, 'admin/finances/liste_revenus.html', context)

@login_required
def ajouter_revenu(request):
    """Ajouter un nouveau revenu"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    if request.method == 'POST':
        form = RevenuForm(request.POST, request.FILES)
        if form.is_valid():
            revenu = form.save(commit=False)
            revenu.utilisateur = request.user
            revenu.save()
            
            # Mettre à jour le solde mensuel
            solde_mensuel, created = SoldeMensuel.objects.get_or_create(
                utilisateur=request.user,
                annee=revenu.date_revenu.year,
                mois=revenu.date_revenu.month
            )
            solde_mensuel.calculer_solde()
            
            messages.success(request, "Revenu enregistré avec succès")
            return redirect('liste_revenus')
    else:
        form = RevenuForm()
    
    return render(request, 'admin/finances/ajouter_revenu.html', {'form': form})

@login_required
def modifier_revenu(request, pk):
    """Modifier un revenu existant"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    revenu = get_object_or_404(Revenu, pk=pk, utilisateur=request.user)
    
    if request.method == 'POST':
        form = RevenuForm(request.POST, request.FILES, instance=revenu)
        if form.is_valid():
            form.save()
            
            # Mettre à jour le solde mensuel
            solde_mensuel, created = SoldeMensuel.objects.get_or_create(
                utilisateur=request.user,
                annee=revenu.date_revenu.year,
                mois=revenu.date_revenu.month
            )
            solde_mensuel.calculer_solde()
            
            messages.success(request, "Revenu modifié avec succès")
            return redirect('liste_revenus')
    else:
        form = RevenuForm(instance=revenu)
    
    return render(request, 'admin/finances/modifier_revenu.html', {'form': form, 'revenu': revenu})

@login_required
def supprimer_revenu(request, pk):
    """Supprimer un revenu"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    revenu = get_object_or_404(Revenu, pk=pk, utilisateur=request.user)
    
    if request.method == 'POST':
        date_revenu = revenu.date_revenu
        revenu.delete()
        
        # Mettre à jour le solde mensuel
        solde_mensuel, created = SoldeMensuel.objects.get_or_create(
            utilisateur=request.user,
            annee=date_revenu.year,
            mois=date_revenu.month
        )
        solde_mensuel.calculer_solde()
        
        messages.success(request, "Revenu supprimé avec succès")
        return redirect('liste_revenus')
    
    return render(request, 'admin/finances/supprimer_revenu.html', {'revenu': revenu})

# ====== GESTION DES FACTURES ======

@login_required
def liste_factures(request):
    """Liste des factures avec filtres"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    factures = Facture.objects.all().order_by('-date_emission')
    
    # Formulaire de recherche
    search_form = FactureSearchForm(request.GET)
    
    if search_form.is_valid():
        cleaned_data = search_form.cleaned_data
        
        if cleaned_data['client']:
            factures = factures.filter(client=cleaned_data['client'])
        
        if cleaned_data['date_debut']:
            factures = factures.filter(date_emission__gte=cleaned_data['date_debut'])
        
        if cleaned_data['date_fin']:
            factures = factures.filter(date_emission__lte=cleaned_data['date_fin'])
        
        if cleaned_data['statut']:
            factures = factures.filter(statut=cleaned_data['statut'])
    
    # Pagination
    paginator = Paginator(factures, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_factures': factures.aggregate(total=Sum('montant_total'))['total'] or 0,
    }
    
    return render(request, 'admin/finances/liste_factures.html', context)

@login_required
def ajouter_facture(request):
    """Ajouter une nouvelle facture"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    if request.method == 'POST':
        form = FactureForm(request.POST)
        if form.is_valid():
            facture = form.save()
            messages.success(request, "Facture créée avec succès")
            return redirect('liste_factures')
    else:
        form = FactureForm()
    
    return render(request, 'admin/finances/ajouter_facture.html', {'form': form})

@login_required
def detail_facture(request, pk):
    """Détails d'une facture"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    facture = get_object_or_404(Facture, pk=pk)
    paiements = facture.paiements.all().order_by('-date_paiement')
    
    context = {
        'facture': facture,
        'paiements': paiements,
    }
    
    return render(request, 'admin/finances/detail_facture.html', context)

# ====== GESTION DES PAIEMENTS CLIENTS ======

@login_required
def ajouter_paiement_client(request, facture_id):
    """Ajouter un paiement client à une facture"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    facture = get_object_or_404(Facture, pk=facture_id)
    
    if request.method == 'POST':
        form = PaiementClientForm(request.POST)
        form.fields['facture'].queryset = Facture.objects.filter(pk=facture_id)
        
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.client = facture.client
            paiement.save()
            
            messages.success(request, "Paiement enregistré avec succès")
            return redirect('detail_facture', pk=facture_id)
    else:
        form = PaiementClientForm(initial={'facture': facture})
        form.fields['facture'].queryset = Facture.objects.filter(pk=facture_id)
    
    return render(request, 'admin/finances/ajouter_paiement_client.html', {
        'form': form,
        'facture': facture
    })

# ====== SUIVI DES SOLDES MENSUELS ======

@login_required
def soldes_mensuels(request):
    """Vue des soldes mensuels"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    soldes = SoldeMensuel.objects.filter(
        utilisateur=request.user
    ).order_by('-annee', '-mois')
    
    # Calculer les totaux annuels
    annees = soldes.values_list('annee', flat=True).distinct()
    stats_annuelles = {}
    
    for annee in annees:
        soldes_annee = soldes.filter(annee=annee)
        stats_annuelles[annee] = {
            'total_depenses': soldes_annee.aggregate(total=Sum('total_depenses'))['total'] or 0,
            'total_revenus': soldes_annee.aggregate(total=Sum('total_revenus'))['total'] or 0,
            'solde_annuel': soldes_annee.aggregate(total=Sum('solde'))['total'] or 0,
        }
    
    context = {
        'soldes': soldes,
        'stats_annuelles': stats_annuelles,
    }
    
    return render(request, 'admin/finances/soldes_mensuels.html', context)

@login_required
def recalculer_soldes(request):
    """Recalculer tous les soldes mensuels"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    if request.method == 'POST':
        # Récupérer toutes les dates uniques de dépenses et revenus
        dates_depenses = Depense.objects.filter(
            utilisateur=request.user,
            statut='validee'
        ).dates('date_depense', 'month')
        
        dates_revenus = Revenu.objects.filter(
            utilisateur=request.user,
            statut='validee'
        ).dates('date_revenu', 'month')
        
        # Combiner les dates
        all_dates = set(dates_depenses).union(set(dates_revenus))
        
        for date in all_dates:
            solde_mensuel, created = SoldeMensuel.objects.get_or_create(
                utilisateur=request.user,
                annee=date.year,
                mois=date.month
            )
            solde_mensuel.calculer_solde()
        
        messages.success(request, f"Soldes recalculés pour {len(all_dates)} mois")
        return redirect('soldes_mensuels')
    
    return render(request, 'admin/finances/recalculer_soldes.html')

# ====== RAPPORTS FINANCIERS ======

@login_required
def generer_rapport_financier(request):
    """Générer un rapport financier"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    if request.method == 'POST':
        form = RapportFinancierForm(request.POST)
        if form.is_valid():
            rapport = form.save(commit=False)
            rapport.utilisateur = request.user
            
            # Calculer les données du rapport
            depenses = Depense.objects.filter(
                utilisateur=request.user,
                date_depense__gte=rapport.periode_debut,
                date_depense__lte=rapport.periode_fin,
                statut='validee'
            ).aggregate(total=Sum('montant'))['total'] or 0
            
            revenus = Revenu.objects.filter(
                utilisateur=request.user,
                date_revenu__gte=rapport.periode_debut,
                date_revenu__lte=rapport.periode_fin,
                statut='validee'
            ).aggregate(total=Sum('montant'))['total'] or 0
            
            rapport.total_depenses = depenses
            rapport.total_revenus = revenus
            rapport.solde_net = revenus - depenses
            
            rapport.save()
            
            # TODO: Générer les fichiers PDF et Excel ici
            
            messages.success(request, "Rapport financier généré avec succès")
            return redirect('liste_rapports_financiers')
    else:
        form = RapportFinancierForm()
    
    return render(request, 'admin/finances/generer_rapport_financier.html', {'form': form})

@login_required
def liste_rapports_financiers(request):
    """Liste des rapports financiers générés"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    rapports = RapportFinancier.objects.filter(
        utilisateur=request.user
    ).order_by('-date_generation')
    
    return render(request, 'admin/finances/liste_rapports_financiers.html', {'rapports': rapports})

# ====== GESTION DES CATÉGORIES ======

@login_required
def categories_depenses(request):
    """Gestion des catégories de dépenses"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    categories = CategorieDepense.objects.all().order_by('nom')
    
    if request.method == 'POST':
        form = CategorieDepenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie ajoutée avec succès")
            return redirect('categories_depenses')
    else:
        form = CategorieDepenseForm()
    
    return render(request, 'admin/finances/categories_depenses.html', {
        'categories': categories,
        'form': form
    })

@login_required
def categories_revenus(request):
    """Gestion des catégories de revenus"""
    if request.user.user_type != '1':
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('home')
    
    categories = CategorieRevenu.objects.all().order_by('nom')
    
    if request.method == 'POST':
        form = CategorieRevenuForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie ajoutée avec succès")
            return redirect('categories_revenus')
    else:
        form = CategorieRevenuForm()
    
    return render(request, 'admin/finances/categories_revenus.html', {
        'categories': categories,
        'form': form
    })
