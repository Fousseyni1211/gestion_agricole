from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import ActiviteAgricole, Culture, Parcelle, FicheConseil, PhotoCulture
from .forms import FicheConseilForm, RecommandationForm

User = get_user_model()

# ==================== GESTION DES ACTIONS AGRICOLES POUR TECHNICIEN AGRONOME ====================

def is_agronome(user):
    """Vérifie si l'utilisateur est un technicien agronome"""
    return hasattr(user, 'profile') and user.profile.role == 'agronome'

@login_required
@user_passes_test(is_agronome)
def tableau_de_bord_agronome(request):
    """
    Affiche le tableau de bord du technicien agronome.
    Cette vue est accessible uniquement aux techniciens agronomes.
    """
    # Statistiques des actions en attente
    arrosages_en_attente = ActiviteAgricole.objects.filter(
        type_activite='arrosage', 
        statut='en_attente_validation'
    ).count()
    
    traitements_en_attente = ActiviteAgricole.objects.filter(
        type_activite='traitement', 
        statut='en_attente_validation'
    ).count()
    
    fertilisations_en_attente = ActiviteAgricole.objects.filter(
        type_activite='fertilisation', 
        statut='en_attente_validation'
    ).count()
    
    # Photos récentes à vérifier
    photos_en_attente = PhotoCulture.objects.filter(statut='en_attente').count()
    
    # Activités récentes
    activites_recentes = ActiviteAgricole.objects.filter(
        statut='en_attente_validation'
    ).select_related('agriculteur', 'parcelle', 'culture').order_by('-date_activite')[:10]
    
    context = {
        'titre': 'Tableau de Bord - Technicien Agronome',
        'arrosages_en_attente': arrosages_en_attente,
        'traitements_en_attente': traitements_en_attente,
        'fertilisations_en_attente': fertilisations_en_attente,
        'photos_en_attente': photos_en_attente,
        'activites_recentes': activites_recentes,
    }
    
    return render(request, 'agronome/tableau_de_bord_agronome.html', context)

@login_required
@user_passes_test(is_agronome)
def validation_arrosages(request):
    """
    Affiche les arrosages en attente de validation.
    """
    arrosages = ActiviteAgricole.objects.filter(
        type_activite='arrosage',
        statut='en_attente_validation'
    ).select_related('agriculteur', 'parcelle', 'culture').order_by('-date_activite')
    
    context = {
        'titre': 'Validation des Arrosages',
        'actions': arrosages,
        'type_action': 'arrosage',
    }
    
    return render(request, 'agronome/validation_actions.html', context)

@login_required
@user_passes_test(is_agronome)
def validation_traitements(request):
    """
    Affiche les traitements en attente de validation.
    """
    traitements = ActiviteAgricole.objects.filter(
        type_activite='traitement',
        statut='en_attente_validation'
    ).select_related('agriculteur', 'parcelle', 'culture').order_by('-date_activite')
    
    context = {
        'titre': 'Validation des Traitements',
        'actions': traitements,
        'type_action': 'traitement',
    }
    
    return render(request, 'agronome/validation_actions.html', context)

@login_required
@user_passes_test(is_agronome)
def validation_fertilisations(request):
    """
    Affiche les fertilisations en attente de validation.
    """
    fertilisations = ActiviteAgricole.objects.filter(
        type_activite='fertilisation',
        statut='en_attente_validation'
    ).select_related('agriculteur', 'parcelle', 'culture').order_by('-date_activite')
    
    context = {
        'titre': 'Validation des Fertilisations',
        'actions': fertilisations,
        'type_action': 'fertilisation',
    }
    
    return render(request, 'agronome/validation_actions.html', context)

@login_required
@user_passes_test(is_agronome)
def valider_action(request, activite_id):
    """
    Valide une action agricole et envoie une recommandation.
    """
    activite = get_object_or_404(ActiviteAgricole, id=activite_id)
    
    if request.method == 'POST':
        form = RecommandationForm(request.POST)
        if form.is_valid():
            recommandation = form.cleaned_data['recommandation']
            
            # Mettre à jour le statut de l'activité
            activite.statut = 'validee'
            activite.validee_par = request.user
            activite.date_validation = timezone.now()
            activite.recommandation = recommandation
            activite.save()
            
            # Envoyer un email à l'agriculteur
            try:
                sujet = f"Validation de votre action agricole - {activite.get_type_activite_display()}"
                message = f"""
Bonjour {activite.agriculteur.farm_name},

Votre action agricole du {activite.date_activite.strftime('%d/%m/%Y')} a été validée par notre technicien agronome.

Type d'action: {activite.get_type_activite_display()}
Parcelle: {activite.parcelle.nom if activite.parcelle else 'Non spécifiée'}
Culture: {activite.culture.nom if activite.culture else 'Non spécifiée'}

Recommandation du technicien:
{recommandation}

Cordialement,
L'équipe technique
                """
                send_mail(
                    sujet,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [activite.agriculteur.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email: {e}")
            
            messages.success(request, f"L'action a été validée et l'email envoyé à l'agriculteur.")
            return redirect('validation_arrosages')
    else:
        form = RecommandationForm()
    
    context = {
        'titre': f'Validation - {activite.get_type_activite_display()}',
        'activite': activite,
        'form': form,
    }
    
    return render(request, 'agronome/validation_action.html', context)

@login_required
@user_passes_test(is_agronome)
def refuser_action(request, activite_id):
    """
    Refuse une action agricole avec un motif.
    """
    activite = get_object_or_404(ActiviteAgricole, id=activite_id)
    
    if request.method == 'POST':
        motif = request.POST.get('motif', '')
        
        if motif:
            activite.statut = 'refusee'
            activite.validee_par = request.user
            activite.date_validation = timezone.now()
            activite.recommandation = motif
            activite.save()
            
            # Envoyer un email à l'agriculteur
            try:
                sujet = f"Action agricole refusée - {activite.get_type_activite_display()}"
                message = f"""
Bonjour {activite.agriculteur.farm_name},

Votre action agricole du {activite.date_activite.strftime('%d/%m/%Y')} a été refusée par notre technicien agronome.

Motif du refus:
{motif}

Merci de prendre en compte ces remarques pour vos prochaines actions.

Cordialement,
L'équipe technique
                """
                send_mail(
                    sujet,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [activite.agriculteur.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email: {e}")
            
            messages.warning(request, f"L'action a été refusée et l'email envoyé à l'agriculteur.")
            return redirect('validation_arrosages')
    
    context = {
        'titre': f'Refus - {activite.get_type_activite_display()}',
        'activite': activite,
    }
    
    return render(request, 'agronome/refus_action.html', context)

@login_required
@user_passes_test(is_agronome)
def verification_photos(request):
    """
    Affiche les photos envoyées par les agriculteurs en attente de vérification.
    """
    photos = PhotoCulture.objects.filter(
        statut='en_attente'
    ).select_related('agriculteur', 'culture', 'parcelle').order_by('-date_envoi')
    
    context = {
        'titre': 'Vérification des Photos',
        'photos': photos,
    }
    
    return render(request, 'agronome/verification_photos.html', context)

@login_required
@user_passes_test(is_agronome)
def valider_photo(request, photo_id):
    """
    Valide une photo de culture.
    """
    photo = get_object_or_404(PhotoCulture, id=photo_id)
    
    if request.method == 'POST':
        commentaire = request.POST.get('commentaire', '')
        
        photo.statut = 'validee'
        photo.validee_par = request.user
        photo.date_validation = timezone.now()
        photo.commentaire = commentaire
        photo.save()
        
        messages.success(request, "La photo a été validée.")
        return redirect('verification_photos')
    
    context = {
        'titre': 'Validation de Photo',
        'photo': photo,
    }
    
    return render(request, 'agronome/validation_photo.html', context)

@login_required
@user_passes_test(is_agronome)
def suivi_sante_cultures(request):
    """
    Affiche un dashboard de suivi de la santé des cultures.
    """
    # Statistiques par culture
    cultures = Culture.objects.all()
    cultures_stats = []
    
    for culture in cultures:
        # Compter les activités récentes pour cette culture
        activites_recentes = ActiviteAgricole.objects.filter(
            culture=culture,
            date_activite__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
        
        # Compter les photos récentes
        photos_recentes = PhotoCulture.objects.filter(
            culture=culture,
            date_envoi__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
        
        cultures_stats.append({
            'culture': culture,
            'activites_recentes': activites_recentes,
            'photos_recentes': photos_recentes,
        })
    
    context = {
        'titre': 'Suivi de la Santé des Cultures',
        'cultures_stats': cultures_stats,
    }
    
    return render(request, 'agronome/suivi_sante_cultures.html', context)

@login_required
@user_passes_test(is_agronome)
def liste_fiches_conseils(request):
    """
    Affiche la liste des fiches-conseils agricoles.
    """
    fiches = FicheConseil.objects.all().order_by('-date_creation')
    
    context = {
        'titre': 'Fiches-Conseils Agricoles',
        'fiches': fiches,
    }
    
    return render(request, 'agronome/liste_fiches_conseils.html', context)

@login_required
@user_passes_test(is_agronome)
def creer_fiche_conseil(request):
    """
    Crée une nouvelle fiche-conseil agricole.
    """
    if request.method == 'POST':
        form = FicheConseilForm(request.POST, request.FILES)
        if form.is_valid():
            fiche = form.save(commit=False)
            fiche.auteur = request.user
            fiche.save()
            
            messages.success(request, "La fiche-conseil a été créée avec succès.")
            return redirect('liste_fiches_conseils')
    else:
        form = FicheConseilForm()
    
    context = {
        'titre': 'Créer une Fiche-Conseil',
        'form': form,
        'action': 'Créer',
    }
    
    return render(request, 'agronome/form_fiche_conseil.html', context)

@login_required
@user_passes_test(is_agronome)
def modifier_fiche_conseil(request, fiche_id):
    """
    Modifie une fiche-conseil existante.
    """
    fiche = get_object_or_404(FicheConseil, id=fiche_id)
    
    if request.method == 'POST':
        form = FicheConseilForm(request.POST, request.FILES, instance=fiche)
        if form.is_valid():
            form.save()
            messages.success(request, "La fiche-conseil a été modifiée avec succès.")
            return redirect('liste_fiches_conseils')
    else:
        form = FicheConseilForm(instance=fiche)
    
    context = {
        'titre': 'Modifier la Fiche-Conseil',
        'form': form,
        'fiche': fiche,
        'action': 'Modifier',
    }
    
    return render(request, 'agronome/form_fiche_conseil.html', context)
