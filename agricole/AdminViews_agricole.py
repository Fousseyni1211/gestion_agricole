from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import HttpResponse

from .models import Culture, Parcelle, ItineraireTechnique, ActiviteAgricole, Agriculteur
from .forms import (
    CultureForm, ParcelleForm, ParcelleAssignationForm, ItineraireTechniqueForm,
    ActiviteAgricoleForm, ActiviteValidationForm
)

User = get_user_model()

# ==================== GESTION DES CULTURES ====================

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def liste_cultures(request):
    """
    Affiche la liste de toutes les cultures.
    Cette vue est accessible uniquement aux gérants.
    """
    cultures = Culture.objects.all().order_by('nom')
    
    context = {
        'cultures': cultures,
        'titre': 'Gestion des cultures',
    }
    
    return render(request, 'admin/cultures/liste_cultures.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def ajouter_culture(request):
    """
    Ajoute une nouvelle culture.
    Cette vue est accessible uniquement aux gérants.
    """
    if request.method == 'POST':
        form = CultureForm(request.POST)
        if form.is_valid():
            culture = form.save()
            messages.success(request, f"La culture '{culture.nom}' a été ajoutée avec succès.")
            return redirect('liste_cultures')
    else:
        form = CultureForm()
    
    context = {
        'form': form,
        'titre': 'Ajouter une culture',
        'action': 'Ajouter',
    }
    
    return render(request, 'admin/cultures/form_culture.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def modifier_culture(request, culture_id):
    """
    Modifie une culture existante.
    Cette vue est accessible uniquement aux gérants.
    """
    culture = get_object_or_404(Culture, id=culture_id)
    
    if request.method == 'POST':
        form = CultureForm(request.POST, instance=culture)
        if form.is_valid():
            form.save()
            messages.success(request, f"La culture '{culture.nom}' a été modifiée avec succès.")
            return redirect('liste_cultures')
    else:
        form = CultureForm(instance=culture)
    
    context = {
        'form': form,
        'culture': culture,
        'titre': 'Modifier une culture',
        'action': 'Modifier',
    }
    
    return render(request, 'admin/cultures/form_culture.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def supprimer_culture(request, culture_id):
    """
    Supprime une culture.
    Cette vue est accessible uniquement aux gérants.
    """
    culture = get_object_or_404(Culture, id=culture_id)
    
    if request.method == 'POST':
        nom_culture = culture.nom
        culture.delete()
        messages.success(request, f"La culture '{nom_culture}' a été supprimée avec succès.")
        return redirect('liste_cultures')
    
    context = {
        'culture': culture,
        'titre': 'Supprimer une culture',
    }
    
    return render(request, 'admin/cultures/confirmer_suppression_culture.html', context)

# ==================== GESTION DES PARCELLES ====================

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def liste_parcelles(request):
    """
    Affiche la liste de toutes les parcelles.
    Cette vue est accessible uniquement aux gérants.
    """
    parcelles = Parcelle.objects.select_related('agriculteur', 'culture_actuelle').order_by('nom')
    
    # Statistiques
    total_parcelles = parcelles.count()
    parcelles_disponibles = parcelles.filter(statut='disponible').count()
    parcelles_occupees = parcelles.filter(statut='occupee').count()
    parcelles_en_maintenance = parcelles.filter(statut='maintenance').count()
    
    context = {
        'parcelles': parcelles,
        'titre': 'Gestion des parcelles',
        'total_parcelles': total_parcelles,
        'parcelles_disponibles': parcelles_disponibles,
        'parcelles_occupees': parcelles_occupees,
        'parcelles_en_maintenance': parcelles_en_maintenance,
    }
    
    return render(request, 'admin/parcelles/liste_parcelles.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def ajouter_parcelle(request):
    """
    Ajoute une nouvelle parcelle.
    Cette vue est accessible uniquement aux gérants.
    """
    if request.method == 'POST':
        form = ParcelleForm(request.POST)
        if form.is_valid():
            parcelle = form.save()
            messages.success(request, f"La parcelle '{parcelle.nom}' a été ajoutée avec succès.")
            return redirect('liste_parcelles')
    else:
        form = ParcelleForm()
    
    context = {
        'form': form,
        'titre': 'Ajouter une parcelle',
        'action': 'Ajouter',
    }
    
    return render(request, 'admin/parcelles/form_parcelle.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def modifier_parcelle(request, parcelle_id):
    """
    Modifie une parcelle existante.
    Cette vue est accessible uniquement aux gérants.
    """
    parcelle = get_object_or_404(Parcelle, id=parcelle_id)
    
    if request.method == 'POST':
        form = ParcelleForm(request.POST, instance=parcelle)
        if form.is_valid():
            form.save()
            messages.success(request, f"La parcelle '{parcelle.nom}' a été modifiée avec succès.")
            return redirect('liste_parcelles')
    else:
        form = ParcelleForm(instance=parcelle)
    
    context = {
        'form': form,
        'parcelle': parcelle,
        'titre': 'Modifier une parcelle',
        'action': 'Modifier',
    }
    
    return render(request, 'admin/parcelles/form_parcelle.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def assigner_parcelle(request, parcelle_id):
    """
    Assigne une parcelle à un agriculteur.
    Cette vue est accessible uniquement aux gérants.
    """
    parcelle = get_object_or_404(Parcelle, id=parcelle_id)
    
    if request.method == 'POST':
        form = ParcelleAssignationForm(request.POST, instance=parcelle)
        if form.is_valid():
            agriculteur = form.cleaned_data.get('agriculteur')
            culture = form.cleaned_data.get('culture_actuelle')
            
            if agriculteur and culture:
                parcelle.assigner_agriculteur(agriculteur, culture)
                messages.success(request, f"La parcelle '{parcelle.nom}' a été assignée à {agriculteur.farm_name} pour la culture {culture.nom}.")
            else:
                parcelle.liberer_parcelle()
                messages.success(request, f"La parcelle '{parcelle.nom}' a été libérée.")
            
            return redirect('liste_parcelles')
    else:
        form = ParcelleAssignationForm(instance=parcelle)
    
    context = {
        'form': form,
        'parcelle': parcelle,
        'titre': 'Assigner une parcelle',
    }
    
    return render(request, 'admin/parcelles/assigner_parcelle.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def supprimer_parcelle(request, parcelle_id):
    """
    Supprime une parcelle.
    Cette vue est accessible uniquement aux gérants.
    """
    parcelle = get_object_or_404(Parcelle, id=parcelle_id)
    
    if request.method == 'POST':
        nom_parcelle = parcelle.nom
        parcelle.delete()
        messages.success(request, f"La parcelle '{nom_parcelle}' a été supprimée avec succès.")
        return redirect('liste_parcelles')
    
    context = {
        'parcelle': parcelle,
        'titre': 'Supprimer une parcelle',
    }
    
    return render(request, 'admin/parcelles/confirmer_suppression_parcelle.html', context)

# ==================== GESTION DES ITINÉRAIRES TECHNIQUES ====================

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def liste_itineraires_techniques(request):
    """
    Affiche la liste de tous les itinéraires techniques.
    Cette vue est accessible uniquement aux gérants.
    """
    itineraires = ItineraireTechnique.objects.select_related('parcelle', 'culture', 'responsable').order_by('-date_planifiee')
    
    context = {
        'itineraires': itineraires,
        'titre': 'Gestion des itinéraires techniques',
    }
    
    return render(request, 'admin/itineraires/liste_itineraires.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def ajouter_itineraire_technique(request):
    """
    Ajoute un nouvel itinéraire technique.
    Cette vue est accessible uniquement aux gérants.
    """
    if request.method == 'POST':
        form = ItineraireTechniqueForm(request.POST)
        if form.is_valid():
            itineraire = form.save()
            messages.success(request, f"L'itinéraire technique pour {itineraire.parcelle.nom} a été ajouté avec succès.")
            return redirect('liste_itineraires_techniques')
    else:
        form = ItineraireTechniqueForm()
    
    context = {
        'form': form,
        'titre': 'Ajouter un itinéraire technique',
        'action': 'Ajouter',
    }
    
    return render(request, 'admin/itineraires/form_itineraire.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def modifier_itineraire_technique(request, itineraire_id):
    """
    Modifie un itinéraire technique existant.
    Cette vue est accessible uniquement aux gérants.
    """
    itineraire = get_object_or_404(ItineraireTechnique, id=itineraire_id)
    
    if request.method == 'POST':
        form = ItineraireTechniqueForm(request.POST, instance=itineraire)
        if form.is_valid():
            form.save()
            messages.success(request, f"L'itinéraire technique a été modifié avec succès.")
            return redirect('liste_itineraires_techniques')
    else:
        form = ItineraireTechniqueForm(instance=itineraire)
    
    context = {
        'form': form,
        'itineraire': itineraire,
        'titre': 'Modifier un itinéraire technique',
        'action': 'Modifier',
    }
    
    return render(request, 'admin/itineraires/form_itineraire.html', context)

# ==================== GESTION DES ACTIVITÉS AGRICOLES ====================

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def liste_activites_agricoles(request):
    """
    Affiche la liste de toutes les activités agricoles en attente de validation.
    Cette vue est accessible uniquement aux gérants.
    """
    activites = ActiviteAgricole.objects.select_related(
        'parcelle', 'culture', 'agriculteur', 'responsable'
    ).filter(statut='en_attente_validation').order_by('-date_planifiee')
    
    context = {
        'activites': activites,
        'titre': 'Validation des activités agricoles',
    }
    
    return render(request, 'admin/activites/liste_activites.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def valider_activite_agricole(request, activite_id):
    """
    Valide ou refuse une activité agricole.
    Cette vue est accessible uniquement aux gérants.
    """
    activite = get_object_or_404(ActiviteAgricole, id=activite_id)
    
    if request.method == 'POST':
        form = ActiviteValidationForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data.get('action')
            motif_refus = form.cleaned_data.get('motif_refus')
            
            if action == 'valider':
                activite.valider_activite(request.user)
                messages.success(request, f"L'activité '{activite.titre}' a été validée avec succès.")
            else:
                activite.refuser_activite(request.user, motif_refus or "Aucun motif spécifié")
                messages.warning(request, f"L'activité '{activite.titre}' a été refusée.")
            
            return redirect('liste_activites_agricoles')
    else:
        form = ActiviteValidationForm()
    
    context = {
        'form': form,
        'activite': activite,
        'titre': 'Validation d\'activité agricole',
    }
    
    return render(request, 'admin/activites/valider_activite.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def tableau_de_bord_agricole(request):
    """
    Affiche le tableau de bord agricole avec les statistiques.
    Cette vue est accessible uniquement aux gérants.
    """
    # Statistiques
    total_cultures = Culture.objects.filter(est_actif=True).count()
    total_parcelles = Parcelle.objects.filter(est_active=True).count()
    parcelles_occupees = Parcelle.objects.filter(statut='occupee').count()
    parcelles_disponibles = Parcelle.objects.filter(statut='disponible').count()
    
    # Activités en attente
    activites_en_attente = ActiviteAgricole.objects.filter(statut='en_attente_validation').count()
    
    # Itinéraires techniques en cours
    itineraires_en_cours = ItineraireTechnique.objects.filter(statut='en_cours').count()
    
    context = {
        'titre': 'Tableau de bord agricole',
        'total_cultures': total_cultures,
        'total_parcelles': total_parcelles,
        'parcelles_occupees': parcelles_occupees,
        'parcelles_disponibles': parcelles_disponibles,
        'activites_en_attente': activites_en_attente,
        'itineraires_en_cours': itineraires_en_cours,
    }
    
    return render(request, 'admin/tableau_de_bord_agricole.html', context)
