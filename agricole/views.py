from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from .models import CustomUser, Client, Agriculteur, Admin, Produit, Commande, Paiement, Service, DemandeService
from datetime import datetime
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
import os, requests
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse, Http404
from decimal import Decimal
from django.urls import reverse
from .models import Notification
import json
import time
from django.views.decorators.csrf import csrf_exempt
from .orange_money import OrangeMoneyAPI

from django.forms import modelformset_factory
from django.forms import inlineformset_factory
from .forms import CommandeForm, DetailCommandeForm
from datetime import timedelta
from .models import Commande, DetailCommande, Produit, Client
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from django.db.models import Sum
from django.conf import settings
from xhtml2pdf import pisa
from .forms import DetailCommandeForm
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.admin.views.decorators import staff_member_required
from .models import (
    CustomUser, Client, Agriculteur, Admin,
    Produit, Commande, Paiement  # adapte si certains modèles n'existent pas
)


def home(request):
    return render(request, 'home.html')

def contact(request):
    return render(request, 'contact.html')

def manage_payments(request):
    # Ta logique ici
    return render(request, 'admin_template/manage_payments.html')
def weather_forecast(request):
    api_key = "ta_clé_api_openweathermap"
    ville = "Bamako"

    url = f"https://api.openweathermap.org/data/2.5/weather?q={ville}&appid={api_key}&units=metric&lang=fr"

    try:
        response = requests.get(url)
        data = response.json()

        weather_data = {
            'ville': ville,
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'].capitalize(),
            'icone': data['weather'][0]['icon'],
            'humidite': data['main']['humidity'],
            'vent': data['wind']['speed']
        }

    except Exception as e:
        weather_data = {
            'ville': ville,
            'error': "Erreur météo",
            'details': str(e)
        }

    return render(request, 'admin/weather_forecast.html', {'weather': weather_data})

def manage_product(request):
    # Ton code ici (ou juste un placeholder)
    return render(request, 'admin_template/manage_product.html')

def manage_users(request):
    # Logic to manage users, e.g., fetching users from the database
    context = {
        'users': User.objects.all(),  # Or whatever logic you need
    }
    return render(request, 'manage_users.html', context)

def manage_orders(request):
    # logique ici
    return render(request, 'admin_template/manage_orders.html')

def landing_page(request):
    return render(request, 'landing.html')  # le nom du fichier HTML

def loginUser(request):
    return render(request, 'login_page.html')

def doLogin(request):
    if request.method != 'POST':
        return redirect('loginUser')  # assure-toi que cette URL existe

    email = request.POST.get('email')
    mot_de_passe = request.POST.get('mot_de_passe')

    if not (email and mot_de_passe):
        messages.error(request, "Veuillez remplir tous les champs.")
        return render(request, 'login_page.html')

    try:
        user_obj = CustomUser.objects.get(email=email)
        user = authenticate(request, username=user_obj.username, password=mot_de_passe)
    except CustomUser.DoesNotExist:
        user = None

    if user is None:
        messages.error(request, "Identifiants invalides.")
        return render(request, 'login_page.html')

    login(request, user)

    # Vérifier le rôle avec plusieurs formats pour compatibilité
    role = user.role.lower() if hasattr(user, 'role') else ''
    user_type = getattr(user, 'user_type', '')
    
    # Redirection basée sur le rôle
    if role in ['agriculteur', '4'] or user_type == '4':
        return redirect('agri_home')
    elif role in ['client', '3'] or user_type == '3':
        return redirect('client_home')
    elif role in ['admin', '1'] or user_type == '1':
        return redirect('gerant_home')

    # Si aucun rôle reconnu, rediriger vers l'accueil avec un message
    messages.warning(request, "Rôle utilisateur non reconnu. Contactez le gérant.")
    return redirect('home')




def registration(request):
    return render(request, 'registration.html')



User = get_user_model()
def doRegistration(request):
    if request.method == "POST":
        prenom = request.POST.get('prénom')
        nom = request.POST.get('nom_de_famille')
        email = request.POST.get('email')
        mot_de_passe = request.POST.get('mot_de_passe')
        confirmer = request.POST.get('confirmerMotDePasse')
        role = request.POST.get('role')

        # Validation simple
        if mot_de_passe != confirmer:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('registration')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return redirect('registration')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Email invalide.")
            return redirect('registration')

        # Création de l'utilisateur avec sécurisation du mot de passe
        user = User(
            first_name=prenom,
            last_name=nom,
            email=email,
            role=role,
            username=email  # Si username est requis
        )
        user.set_password(mot_de_passe)  # 🔐 Hashe le mot de passe !
        user.save()

        messages.success(request, "Inscription réussie ! Vous pouvez maintenant vous connecter.")
        return redirect('login')

    return render(request, 'registration.html')  # Ton template d'inscription

    # Création de l'utilisateur
    user = CustomUser(
        username=username,
        email=email_id,
        # prénom=prénom,
        # nom_de_famille=nom_de_famille,
        user_type=user_type
    )
    user.set_password(mot_de_passe)  # HASH le mot de passe
    user.save()

    # Création du profil spécifique
    if user_type == CustomUser.CLIENT:
        Client.objects.create(admin=user)
    elif user_type == CustomUser.AGRICULTEUR:
        Agriculteur.objects.create(admin=user)
    elif user_type == CustomUser.ADMIN:
        Admin.objects.create(admin=user)

    messages.success(request, 'Registration successful! You can now log in.')
    return redirect('login')


def logout_user(request):
    logout(request)
    response = redirect('login')  # Redirection vers la vue login
    # Empêcher le cache du navigateur pour éviter le retour aux pages gérant
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
def get_user_type_from_email(email_id):
    """
    Extrait le type d'utilisateur depuis l'email. Ex: 'john.client@exemple.com' => 'client'
    """
    try:
        local_part = email_id.split('@')[0]  # john.client
        user_role = local_part.split('.')[1]  # client
        return CustomUser.EMAIL_TO_USER_TYPE_MAP.get(user_role.lower())
    except (IndexError, AttributeError):
        return None
    
    
def redirect_user_by_role(request):
    if request.user.role == 'admin':
        return redirect('gerant_home')
    elif request.user.role == 'client':
        return redirect('client_home')
    elif request.user.role == 'agriculteur':
        return redirect('agri_home')
    else:
        return redirect('page_par_defaut')
    
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        full_message = f"Message de {name} ({email})\n\n{message}"

        try:
            send_mail(
                subject,
                full_message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'webmaster@localhost',
                [settings.ADMIN_EMAIL if hasattr(settings, 'ADMIN_EMAIL') else 'admin@localhost'],
                fail_silently=False,
            )
            messages.success(request, "Votre message a bien été envoyé. Merci de nous avoir contactés.")
            return redirect('contact')
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")

    return render(request, 'contact.html')
def services_view(request):
    return render(request, 'services.html')

# Vérifie que l'utilisateur est staff/gérant
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)
# Vérifier que c'est un gérant (staff)
def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
@login_required
def liste_clients(request):
    User = get_user_model()
    
    # Afficher tous les clients en ignorant la casse de "Client"
    clients = User.objects.filter(role__iexact='Client').order_by('last_name', 'first_name')

    return render(request, 'admin/liste_clients.html', {
        'clients': clients
    })
@admin_required
def activer_client(request, client_id):
    client = get_object_or_404(CustomUser, id=client_id, role='Client')
    client.is_active = True
    client.save()
    messages.success(request, f"Le client {client.username} a été activé.")
    return redirect('liste_clients')

@admin_required
def desactiver_client(request, client_id):
    client = get_object_or_404(CustomUser, id=client_id, role='Client')
    client.is_active = False
    client.save()
    messages.success(request, f"Le client {client.username} a été désactivé.")
    return redirect('liste_clients')
# class CustomLoginView(LoginView):
#     template_name = 'registration/login.html'  # ou ton template
#     redirect_authenticated_user = True  # si tu veux rediriger les déjà connectés

    def form_invalid(self, form):
        # Si formulaire invalide (identifiants incorrects), détecter si c'est un client désactivé
        username = form.cleaned_data.get('username')
        if username:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
                if not user.is_active:
                    messages.error(self.request, "Votre compte est désactivé. Veuillez contacter le gérant.")
                    return self.render_to_response(self.get_context_data(form=form))
            except User.DoesNotExist:
                pass
        # Cas général erreur login
        messages.error(self.request, "Nom d'utilisateur ou mot de passe incorrect.")
        return super().form_invalid(form)
    

def generer_facture_pdf(request, commande_id):
    # Débogage pour voir l'ID de la commande demandée
    print(f"Génération de facture PDF pour la commande ID={commande_id}")
    
    try:
        # Recherche plus flexible de la commande
        commande = Commande.objects.select_related('client').get(id=commande_id)
        print(f"Commande trouvée: ID={commande.id}, Client={commande.client.username}")
        
        # Utiliser le template amélioré
        template = get_template("admin/facture_pdf.html")
        context = {
            'commande': commande,
            'logo_path': settings.STATIC_URL + 'dist/img/logo.png',
        }

        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{commande.id}.pdf"'

        pisa_status = pisa.CreatePDF(
            src=html, dest=response,
            encoding='UTF-8', link_callback=link_callback
        )
        if pisa_status.err:
            print(f"Erreur lors de la génération du PDF: {pisa_status.err}")
            return HttpResponse('Erreur lors de la génération du PDF', status=500)
        
        return response
    except Commande.DoesNotExist:
        print(f"Erreur: Commande avec ID={commande_id} introuvable")
        return HttpResponse(f"Commande introuvable (ID={commande_id})", status=404)
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        return HttpResponse(f"Erreur: {str(e)}", status=500)


def link_callback(uri, rel):
    if uri.startswith(settings.STATIC_URL):
        relative_path = uri.replace(settings.STATIC_URL, "")
        # Try STATIC_ROOT first (post-collectstatic)
        if getattr(settings, 'STATIC_ROOT', None):
            path = os.path.join(settings.STATIC_ROOT, relative_path)
            if os.path.isfile(path):
                return path
        # Fallback: look into STATICFILES_DIRS during development
        for static_dir in getattr(settings, 'STATICFILES_DIRS', []):
            candidate = os.path.join(static_dir, relative_path)
            if os.path.isfile(candidate):
                return candidate
        return None
    elif uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
        return path if os.path.isfile(path) else None
    else:
        return uri
def is_admin(user):
    return user.is_authenticated and user.is_superuser  # ou user.role == 'Admin' si tu as un champ `role`

@user_passes_test(is_admin)
@login_required
def liste_agriculteurs(request):
    User = get_user_model()

    # Récupérer les agriculteurs avec les champs nécessaires
    agriculteurs = User.objects.filter(role__iexact='Agriculteur').order_by('last_name', 'first_name')
    
    # Calculer les statistiques de genre
    stats = {
        'male': agriculteurs.filter(gender='M').count(),
        'female': agriculteurs.filter(gender='F').count(),
        'other': agriculteurs.exclude(gender__in=['M', 'F']).count(),
        'total': agriculteurs.count()
    }

    return render(request, 'admin/liste_agriculteurs.html', {
        'agriculteurs': agriculteurs,
        'gender_stats': stats
    })

def is_admin(user):
    return user.is_authenticated and user.is_superuser  # ou user.role == 'Admin'

@login_required
def passer_commande(request):
    # Si tu crées une nouvelle commande, instancie un nouvel objet vide
    commande = Commande()

    # Création du formset inline lié à Commande et DetailCommande
    DetailCommandeFormSet = inlineformset_factory(
        Commande,
        DetailCommande,
        form=DetailCommandeForm,
        extra=1,
        can_delete=True
    )

    if request.method == 'POST':
        form = CommandeForm(request.POST, instance=commande)
        formset = DetailCommandeFormSet(request.POST, instance=commande)

        if form.is_valid() and formset.is_valid():
            # Sauvegarde de la commande (parent)
            commande = form.save()

            # Sauvegarde des détails liés à la commande
            formset.instance = commande
            formset.save()

            # Redirige vers une page de confirmation ou liste des commandes
            return redirect('liste_commandes')
    else:
        form = CommandeForm(instance=commande)
        formset = DetailCommandeFormSet(instance=commande)

    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'agriculteur/passer_commande.html', context)


@login_required
def suivi_commandes(request):
    commandes = Commande.objects.filter(client=request.user)\
                                .order_by('-date_commande')
    return render(request, 'commandes/suivi_commandes.html',
                  {'commandes': commandes})


@login_required
def detail_commande(request, pk):
    commande = get_object_or_404(
        Commande.objects.prefetch_related('details__produit'),
        pk=pk, client=request.user
    )
    return render(request, 'commande/detail_commande.html',
                  {'commande': commande})
DetailCommandeFormSet = modelformset_factory(
    DetailCommande,
    form=DetailCommandeForm,
    extra=1,
    can_delete=True
)

@login_required
def facture_pdf(request, pk):
    # Débogage pour voir l'ID de la commande demandée
    print(f"Génération de facture PDF pour la commande ID={pk}")
    
    try:
        # Recherche plus flexible de la commande (sans vérifier le client)
        commande = Commande.objects.get(pk=pk)
        print(f"Commande trouvée: ID={commande.id}, Client={commande.client.username}")
        
        # Vérifier si l'utilisateur est admin ou propriétaire de la commande
        if request.user.is_staff or request.user.is_superuser or commande.client == request.user:
            # Utiliser le template admin/facture_pdf.html qui est le seul disponible
            template_path = 'admin/facture_pdf.html'

            # Fournir le logo via STATIC_URL pour résolution par link_callback
            html = render_to_string(template_path, {
                'commande': commande,
                'logo_path': settings.STATIC_URL + 'dist/img/logo.png',
            })
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="facture_{commande.pk}.pdf"'

            # Utiliser link_callback pour que xhtml2pdf résolve les URLs statiques/médias
            pisa_status = pisa.CreatePDF(src=html, dest=response, encoding='UTF-8', link_callback=link_callback)
            if pisa_status.err:
                print(f"Erreur lors de la génération du PDF: {pisa_status.err}")
                return HttpResponse('Erreur lors de la génération du PDF', status=500)
            
            return response
        else:
            print(f"Accès non autorisé: l'utilisateur {request.user.username} n'est pas propriétaire de la commande")
            return HttpResponse("Vous n'êtes pas autorisé à accéder à cette facture", status=403)
    
    except Commande.DoesNotExist:
        print(f"Erreur: Commande avec ID={pk} introuvable")
        return HttpResponse(f"Commande introuvable (ID={pk})", status=404)
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        return HttpResponse(f"Erreur: {str(e)}", status=500)

@login_required
def activer_agriculteur(request, user_id):
    agriculteur = get_object_or_404(CustomUser, id=user_id, role__iexact='Agriculteur')
    agriculteur.is_active = True
    agriculteur.save()
    messages.success(request, f"L’agriculteur {agriculteur.get_full_name()} a été activé.")
    return redirect('liste_agriculteurs')

@login_required
def desactiver_agriculteur(request, user_id):
    agriculteur = get_object_or_404(CustomUser, id=user_id, role__iexact='Agriculteur')
    agriculteur.is_active = False
    agriculteur.save()
    messages.warning(request, f"L’agriculteur {agriculteur.get_full_name()} a été désactivé.")
    return redirect('liste_agriculteurs')
def connexion_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('agri_home')  # ou agri_home selon le rôle
        else:
            messages.error(request, 'Identifiants invalides')

    return render(request, 'login_page.html')
@login_required
def location_materiel(request):
    return render(request, 'agriculteur/location_materiel.html')
@staff_member_required
def gestion_reservations(request):
    # Lister toutes les réservations non validées
    reservations = ReservationMateriel.objects.filter(validee=False).order_by('-date_demande')
    return render(request, 'admin/gestion_reservations.html', {'reservations': reservations})
@staff_member_required
def valider_reservation(request, reservation_id):
    reservation = get_object_or_404(ReservationMateriel, id=reservation_id)
    reservation.validee = True
    reservation.save()

    # Notifier le client par email
    subject = "Votre réservation a été validée"
    message = (
        f"Bonjour {reservation.client.username},\n\n"
        f"Votre réservation du matériel '{reservation.materiel.nom}' du {reservation.date_debut} au {reservation.date_fin} a été validée.\n"
        "Merci pour votre confiance.\n\nCordialement,\nL'équipe"
    )
    reservation.client.email and send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [reservation.client.email])

    messages.success(request, "Réservation validée avec succès.")
    return redirect('gestion_reservations')


@staff_member_required
def annuler_reservation(request, reservation_id):
    reservation = get_object_or_404(ReservationMateriel, id=reservation_id)

    # Notifier le client par email
    subject = "Votre réservation a été annulée"
    message = (
        f"Bonjour {reservation.client.username},\n\n"
        f"Votre réservation du matériel '{reservation.materiel.nom}' du {reservation.date_debut} au {reservation.date_fin} a été annulée.\n"
        "Nous restons à votre disposition.\n\nCordialement,\nL'équipe"
    )
    reservation.client.email and send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [reservation.client.email])

    reservation.delete()

    messages.success(request, "Réservation annulée et supprimée.")
    return redirect('gestion_reservations')

def is_admin(user):
    return user.is_staff  # ou ton propre test de rôle

@login_required
def passer_commande(request):
    """
    Page client pour passer commande. En POST on accepte produits[] (ids), quantite[].
    Le client est automatiquement l'utilisateur connecté.
    """
    # Utiliser directement l'utilisateur connecté comme client
    client = request.user
    
    # Récupérer uniquement les produits disponibles en stock
    produits = Produit.objects.filter(quantite__gt=0)

    if request.method == 'POST':
        produits_ids = request.POST.getlist('produits[]')
        quantites = request.POST.getlist('quantite[]')

        if not produits_ids or not quantites:
            return JsonResponse({'success': False, 'error': 'Données manquantes.'})

        if len(produits_ids) != len(quantites):
            return JsonResponse({'success': False, 'error': 'Lignes incohérentes.'})

        commande = Commande.objects.create(client=client, date_commande=timezone.now(), statut='en_attente', total=Decimal('0.00'))

        total = Decimal('0.00')
        for p_id, q_str in zip(produits_ids, quantites):
            try:
                prod = Produit.objects.get(id=int(p_id))
                q = int(q_str)
                if q <= 0:
                    raise ValueError("Quantité invalide.")
                # NOTE: on NE décrémente pas le stock maintenant (on le fait à la validation admin)
                dc = DetailCommande.objects.create(
                    commande=commande,
                    produit=prod,
                    quantite=q,
                    prix_unitaire=prod.prix_unitaire
                )
                total += dc.sous_total()
            except Exception as e:
                commande.delete()
                return JsonResponse({'success': False, 'error': str(e)})

        commande.total = total
        commande.save()
        
        # Créer une notification pour tous les gérants
        admins = CustomUser.objects.filter(role='Admin')
        produits_text = ", ".join([f"{p.nom_produit} (x{q})" for p, q in
                                  [(Produit.objects.get(id=int(p_id)), int(q_str))
                                   for p_id, q_str in zip(produits_ids, quantites)]])
        
        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=f"Nouvelle commande #{commande.id} de {client.username}: {produits_text}"
            )
        
        return JsonResponse({'success': True, 'redirect_url': reverse('client_commandes')})

    # GET
    return render(request, 'commande/passer_commande.html', {
        'produits': produits,
        'user': client
    })

@login_required
def client_commandes(request):
    """Afficher uniquement les commandes du client connecté."""
    client = request.user
    commandes = Commande.objects.filter(client=client).prefetch_related('details__produit').order_by('-date_commande')
    return render(request, 'commande/mes_commandes.html', {'commandes': commandes})

@user_passes_test(is_admin)
def admin_liste_commandes(request):
    """Liste gérant des commandes avec filtres et pagination, rendu unifié."""
    # Base queryset
    commandes = Commande.objects.all().order_by('-date_commande')

    # Filtrage par statut (inclut 'validee')
    statut = request.GET.get('statut')
    if statut:
        commandes = commandes.filter(statut=statut)

    # Filtrage par client
    client_id = request.GET.get('client')
    if client_id:
        commandes = commandes.filter(client_id=client_id)

    # Pagination (10 par page)
    from django.core.paginator import Paginator
    paginator = Paginator(commandes, 10)
    page = request.GET.get('page')
    commandes_page = paginator.get_page(page)

    # Liste des clients pour le filtre
    clients = CustomUser.objects.filter(role__iexact='Client')

    context = {
        'commandes': commandes_page,
        'clients': clients,
        'titre': 'Liste des commandes',
        'statut_filtre': statut,
        'client_filtre': client_id,
    }

    # Utiliser le même template unifié
    return render(request, 'admin/liste_commandes.html', context)

@user_passes_test(is_admin)
@require_POST
def admin_valider_commande(request, commande_id):
    """Valide une commande payée: vérifie stock et décrémente si OK."""
    commande = get_object_or_404(Commande, id=commande_id, statut='payee_en_attente')
    
    # Vérifier le stock pour chaque ligne
    insuffisances = []
    for ligne in commande.details.select_related('produit'):
        if ligne.quantite > ligne.produit.quantite:
            insuffisances.append(f"{ligne.produit.nom_produit}: dispo {ligne.produit.quantite}, demandé {ligne.quantite}")

    if insuffisances:
        return JsonResponse({'success': False, 'error': 'Stock insuffisant pour: ' + '; '.join(insuffisances)})

    # Décrémenter le stock et valider
    for ligne in commande.details.all():
        produit = ligne.produit
        produit.quantite -= ligne.quantite
        produit.save()

    commande.statut = 'validee'
    commande.save()
    
    # Créer une notification pour le client
    client = commande.client
    produits_text = ", ".join([f"{detail.produit.nom_produit} (x{detail.quantite})"
                              for detail in commande.details.all()[:3]])
    
    if commande.details.count() > 3:
        produits_text += f" et {commande.details.count() - 3} autres produits"
    
    Notification.objects.create(
        user=client,
        message=f"Votre commande #{commande.id} a été validée et est en préparation."
    )
    
    messages.success(request, f"Commande #{commande.id} validée avec succès.")
    
    return redirect('gerant_commandes')

@user_passes_test(is_admin)
@require_POST
def admin_update_order_status(request, commande_id):
    """Met à jour le statut d'une commande."""
    try:
        commande = Commande.objects.get(id=commande_id)
        nouveau_statut = request.POST.get('statut')

        if nouveau_statut in [choix[0] for choix in Commande.STATUTS]:
            commande.statut = nouveau_statut
            commande.save()
            messages.success(request, f"Le statut de la commande #{commande.id} a été mis à jour.")
            # Notifier le client si la commande est prête à être payée
            if nouveau_statut == 'en_attente_paiement':
                Notification.objects.create(
                    user=commande.client,
                    message=f"Votre commande #{commande.id} a été validée. Vous pouvez maintenant procéder au paiement."
                )
            # Réponse AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
        else:
            messages.error(request, "Statut invalide.")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Statut invalide.'})
    except Commande.DoesNotExist:
        messages.error(request, "Commande non trouvée.")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Commande non trouvée.'})
    # Redirection non-AJAX: revenir à la page précédente ou racine
    return redirect(request.META.get('HTTP_REFERER', '/'))

@user_passes_test(is_admin)
@require_POST
def admin_supprimer_commande(request, commande_id):
    """Supprime une commande côté gérant (staff). Cascade sur ses détails."""
    try:
        commande = get_object_or_404(Commande, id=commande_id)
        commande.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        messages.success(request, f"Commande #{commande_id} supprimée.")
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, f"Suppression impossible: {e}")
    return redirect(request.META.get('HTTP_REFERER', '/'))

@user_passes_test(is_admin)
@require_POST
def admin_update_order_status(request, commande_id):
    """Met à jour le statut d'une commande."""
    try:
        commande = Commande.objects.get(id=commande_id)
        nouveau_statut = request.POST.get('statut')

        if nouveau_statut in [choix[0] for choix in Commande.STATUTS]:
            commande.statut = nouveau_statut
            commande.save()
            messages.success(request, f"Le statut de la commande #{commande.id} a été mis à jour.")
            # Notifier le client si la commande est prête à être payée
            if nouveau_statut == 'en_attente_paiement':
                Notification.objects.create(
                    user=commande.client,
                    message=f"Votre commande #{commande.id} a été validée. Vous pouvez maintenant procéder au paiement."
                )
        else:
            messages.error(request, "Statut invalide.")

    except Commande.DoesNotExist:
        messages.error(request, "Commande non trouvée.")
    
    return redirect('admin_commandes')

@user_passes_test(is_admin)
@require_POST
def admin_update_order_status(request, commande_id):
    """Met à jour le statut d'une commande."""
    try:
        commande = Commande.objects.get(id=commande_id)
        nouveau_statut = request.POST.get('statut')

        if nouveau_statut in [choix[0] for choix in Commande.STATUTS]:
            commande.statut = nouveau_statut
            commande.save()
            messages.success(request, f"Le statut de la commande #{commande.id} a été mis à jour.")
            # Notifier le client si la commande est prête à être payée
            if nouveau_statut == 'en_attente_paiement':
                Notification.objects.create(
                    user=commande.client,
                    message=f"Votre commande #{commande.id} a été validée. Vous pouvez maintenant procéder au paiement."
                )
        else:
            messages.error(request, "Statut invalide.")

    except Commande.DoesNotExist:
        messages.error(request, "Commande non trouvée.")
    
    return redirect('admin_commandes')

@user_passes_test(is_admin)
@require_POST
def admin_update_order_status(request, commande_id):
    """Met à jour le statut d'une commande."""
    try:
        commande = Commande.objects.get(id=commande_id)
        nouveau_statut = request.POST.get('statut')

        if nouveau_statut in [choix[0] for choix in Commande.STATUTS]:
            commande.statut = nouveau_statut
            commande.save()
            messages.success(request, f"Le statut de la commande #{commande.id} a été mis à jour.")
            # Notifier le client si la commande est prête à être payée
            if nouveau_statut == 'en_attente_paiement':
                Notification.objects.create(
                    user=commande.client,
                    message=f"Votre commande #{commande.id} a été validée. Vous pouvez maintenant procéder au paiement."
                )
        else:
            messages.error(request, "Statut invalide.")

    except Commande.DoesNotExist:
        messages.error(request, "Commande non trouvée.")
    
    return redirect('admin_commandes')

@user_passes_test(is_admin)
@require_POST
def admin_annuler_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    commande.statut = 'annulee'
    commande.save()
    return JsonResponse({'success': True})

@login_required
def export_commande_pdf(request, commande_id):
    # Exemple simple: tu peux intégrer reportlab / weasyprint pour vrai PDF
    commande = get_object_or_404(Commande, id=commande_id)
    if commande.client.admin != request.user and not request.user.is_staff:
        return HttpResponse("Interdit", status=403)
    text = f"Facture commande #{commande.id}\nClient: {commande.client}\nTotal: {commande.total}\nDétails:\n"
    for d in commande.details.all():
        text += f"- {d.produit.nom_produit} x{d.quantite} = {d.sous_total}\n"
    response = HttpResponse(text, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename=commande_{commande.id}.txt'
    return response

@user_passes_test(is_admin)
def admin_notifications(request):
    """Affiche les notifications pour l'administrateur."""
    # Récupérer les notifications non lues de l'administrateur
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Récupérer les commandes en attente
    commandes_en_attente = Commande.objects.filter(statut='en_attente').select_related('client').prefetch_related('details__produit')
    
    return render(request, 'admin/notifications.html', {
        'notifications': notifications,
        'commandes_en_attente': commandes_en_attente
    })

@user_passes_test(is_admin)
def marquer_notification_lue(request, notification_id):
    """Marque une notification comme lue."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()  # Ou vous pourriez ajouter un champ 'lue' et le mettre à True
    return redirect('admin_notifications')

def demande_service(request):
    """
    Vue pour traiter les demandes de service des clients.
    Accessible via le formulaire de la page services.html.
    """
    if request.method == 'POST':
        # Vérifier si l'utilisateur est connecté
        if not request.user.is_authenticated:
            messages.error(request, "Vous devez être connecté pour demander un service.")
            return redirect('login')
        
        # Récupérer les données du formulaire
        service_type = request.POST.get('service')
        date_souhaitee = request.POST.get('date_souhaitee')
        message = request.POST.get('message')
        
        # Validation des données
        if not service_type or not message:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return redirect('services')

# --- Vues pour le Paiement Orange Money ---

@login_required
def pay_for_order(request, commande_id):
    """Affiche la page de paiement pour une commande spécifique."""
    commande = get_object_or_404(Commande, id=commande_id, client=request.user)
    context = {
        'commande': commande
    }
    return render(request, 'client/paiement_commande.html', context)

@login_required
def confirmation_paiement(request, commande_id):
    """Affiche la page de confirmation après un paiement réussi."""
    commande = get_object_or_404(Commande, id=commande_id, client=request.user)
    
    # Mettre à jour le statut de la commande si nécessaire
    if commande.statut == 'en_attente_paiement':
        commande.statut = 'validee'
        commande.save()
    
    context = {
        'commande': commande,
        'payment_success': True
    }
    return render(request, 'client/confirmation_paiement.html', context)

@login_required
@require_POST
def initiate_payment_view(request):
    """Initialise la transaction auprès de l'API Orange Money."""
    commande_id = request.POST.get('commande_id')
    commande = get_object_or_404(Commande, id=commande_id, client=request.user)

    om_api = OrangeMoneyAPI()
    
    # Construire les URLs absolues pour les retours de l'API
    return_url = request.build_absolute_uri(reverse('payment_success'))
    cancel_url = request.build_absolute_uri(reverse('payment_cancel'))
    notify_url = request.build_absolute_uri(reverse('payment_webhook'))

    response_data = om_api.initiate_payment(
        amount=int(commande.total),
        order_id=str(commande.id),
        return_url=return_url,
        cancel_url=cancel_url,
        notify_url=notify_url
    )

    if 'payment_url' in response_data:
        # Créer ou mettre à jour l'enregistrement de paiement
        Paiement.objects.update_or_create(
            commande=commande,
            defaults={
                'montant': commande.total,
                'methode': 'Orange Money',
                'statut': 'en_attente',
                'pay_token': response_data.get('pay_token') # Important pour le webhook
            }
        )
        return JsonResponse({'success': True, 'payment_url': response_data['payment_url']})
    else:
        error_message = response_data.get('description', 'Erreur inconnue lors de l\'initiation du paiement.')
        return JsonResponse({'success': False, 'error': error_message})

@login_required
def payment_success_view(request):
    """Page affichée après une redirection de succès depuis Orange Money."""
    messages.success(request, "Votre paiement a été initié. Vous recevrez une notification de confirmation.")
    return redirect('client_commandes')

@login_required
def payment_cancel_view(request):
    """Page affichée après une annulation depuis Orange Money."""
    messages.warning(request, "Le processus de paiement a été annulé.")
    return redirect('client_commandes')

@csrf_exempt
@require_POST
def payment_webhook(request):
    """Webhook pour recevoir les notifications de statut de paiement d'Orange Money."""
    try:
        data = json.loads(request.body)
        status = data.get('status')
        order_id = data.get('order_id')

        if not all([status, order_id]):
            return JsonResponse({'error': 'Données de webhook invalides'}, status=400)

        paiement = get_object_or_404(Paiement, commande__id=order_id)

        if status == 'SUCCESS':
            paiement.statut = 'valide'
            paiement.commande.statut = 'payee_en_attente'
            paiement.transaction_id = data.get('txnid', '')
            Notification.objects.create(
                user=paiement.commande.client,
                message=f"Paiement confirmé pour la commande #{paiement.commande.id}. En attente de validation par le gérant."
            )
        else:
            paiement.statut = 'echoue'
            Notification.objects.create(
                user=paiement.commande.client,
                message=f"Le paiement pour la commande #{paiement.commande.id} a échoué."
            )
        
        paiement.save()
        paiement.commande.save()

        return JsonResponse({'status': 'ok'})

    except (json.JSONDecodeError, Paiement.DoesNotExist) as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Erreur interne du serveur'}, status=500)
    return HttpResponse(status=405)  # Method Not Allowed

def mes_demandes_service(request):
    """
    Vue pour afficher les demandes de service d'un client.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Vous devez être connecté pour voir vos demandes de service.")
        return redirect('login')
    
    # Récupérer les demandes de service du client
    demandes = DemandeService.objects.filter(client=request.user).order_by('-date_demande')
    
    return render(request, 'client/mes_demandes_service.html', {
        'demandes': demandes
    })

@user_passes_test(is_admin)
def admin_liste_demandes_service(request):
    """
    Vue pour afficher toutes les demandes de service pour l'administrateur.
    """
    # Filtrer par statut si spécifié
    statut = request.GET.get('statut')
    if statut:
        demandes = DemandeService.objects.filter(statut=statut).select_related('client', 'service').order_by('-date_demande')
    else:
        demandes = DemandeService.objects.all().select_related('client', 'service').order_by('-date_demande')
    
    return render(request, 'admin/liste_demandes_service.html', {
        'demandes': demandes,
        'statuts': DemandeService.STATUTS
    })

@user_passes_test(is_admin)
def admin_detail_demande_service(request, demande_id):
    """
    Vue pour afficher le détail d'une demande de service pour l'administrateur.
    """
    demande = get_object_or_404(DemandeService, id=demande_id)
    
    if request.method == 'POST':
        # Mettre à jour le statut de la demande
        nouveau_statut = request.POST.get('statut')
        commentaire = request.POST.get('commentaire_admin')
        
        if nouveau_statut in dict(DemandeService.STATUTS):
            ancien_statut = demande.statut
            demande.statut = nouveau_statut
            demande.commentaire_admin = commentaire
            demande.save()
            
            # Notifier le client du changement de statut
            Notification.objects.create(
                user=demande.client,
                message=f"Le statut de votre demande de service '{demande.service.nom}' est passé de '{dict(DemandeService.STATUTS).get(ancien_statut)}' à '{dict(DemandeService.STATUTS).get(nouveau_statut)}'."
            )
            
            messages.success(request, f"Le statut de la demande a été mis à jour : {dict(DemandeService.STATUTS).get(nouveau_statut)}")
        else:
            messages.error(request, "Statut invalide.")
    
    return render(request, 'admin/detail_demande_service.html', {
        'demande': demande,
        'statuts': DemandeService.STATUTS
    })

# Payment management views for manager
@user_passes_test(is_admin)
@require_POST
def gerant_valider_paiement(request, paiement_id):
    """Valider un paiement par le gérant."""
    try:
        paiement = get_object_or_404(Paiement, id=paiement_id)
        paiement.payment_status = 'Validated'
        paiement.save()
        
        # Mettre à jour le statut de la commande
        paiement.commande.statut = 'payee_en_attente'
        paiement.commande.save()
        
        # Créer une notification pour le client
        Notification.objects.create(
            user=paiement.commande.client,
            message=f"Votre paiement pour la commande #{paiement.commande.id} a été validé."
        )
        
        messages.success(request, f"Paiement #{paiement_id} validé avec succès.")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('gerant_commandes')
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la validation du paiement: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        return redirect('gerant_commandes')

@user_passes_test(is_admin)
@require_POST
def gerant_rejeter_paiement(request, paiement_id):
    """Rejeter un paiement par le gérant."""
    try:
        paiement = get_object_or_404(Paiement, id=paiement_id)
        paiement.payment_status = 'Rejected'
        paiement.save()
        
        # Mettre à jour le statut de la commande
        paiement.commande.statut = 'paiement_echoue'
        paiement.commande.save()
        
        # Créer une notification pour le client
        Notification.objects.create(
            user=paiement.commande.client,
            message=f"Votre paiement pour la commande #{paiement.commande.id} a été rejeté. Veuillez contacter le support."
        )
        
        messages.success(request, f"Paiement #{paiement_id} rejeté.")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('gerant_commandes')
        
    except Exception as e:
        messages.error(request, f"Erreur lors du rejet du paiement: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        return redirect('gerant_commandes')

@user_passes_test(is_admin)
def gerant_liste_paiements(request):
    """Liste de tous les paiements pour le gérant."""
    paiements = Paiement.objects.select_related('commande__client').order_by('-created_at')
    
    # Filtrage par statut
    statut = request.GET.get('statut')
    if statut:
        paiements = paiements.filter(payment_status=statut)
    
    # Filtrage par méthode de paiement
    methode = request.GET.get('methode')
    if methode:
        paiements = paiements.filter(payment_method=methode)
    
    context = {
        'paiements': paiements,
        'statut_filtre': statut,
        'methode_filtre': methode,
    }
    
    return render(request, 'admin/liste_paiements.html', context)

@user_passes_test(is_admin)
def gerant_tableau_de_bord(request):
    """Tableau de bord des ventes et statistiques pour le gérant."""
    from django.db.models import Sum, Count, Avg
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Périodes pour les statistiques
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Statistiques générales
    total_commandes = Commande.objects.count()
    total_revenu = Commande.objects.filter(statut='payee').aggregate(total=Sum('total'))['total'] or 0
    commandes_en_attente = Commande.objects.filter(statut='en_attente').count()
    commandes_validees = Commande.objects.filter(statut='validee').count()
    commandes_livrees = Commande.objects.filter(statut='livree').count()
    
    # Statistiques du mois en cours
    commandes_mois = Commande.objects.filter(date_commande__gte=this_month_start)
    revenu_mois = commandes_mois.filter(statut='payee').aggregate(total=Sum('total'))['total'] or 0
    nb_commandes_mois = commandes_mois.count()
    
    # Statistiques du mois précédent
    commandes_mois_precedent = Commande.objects.filter(
        date_commande__gte=last_month_start,
        date_commande__lt=this_month_start
    )
    revenu_mois_precedent = commandes_mois_precedent.filter(statut='payee').aggregate(total=Sum('total'))['total'] or 0
    nb_commandes_mois_precedent = commandes_mois_precedent.count()
    
    # Top produits vendus
    top_produits = (
        DetailCommande.objects
        .values('produit__nom_produit')
        .annotate(total_vendu=Sum('quantite'), total_revenu=Sum('prix'))
        .order_by('-total_vendu')[:10]
    )
    
    # Top clients
    top_clients = (
        Commande.objects
        .values('client__username', 'client__first_name', 'client__last_name')
        .annotate(nb_commandes=Count('id'), total_depense=Sum('total'))
        .filter(statut__in=['payee', 'validee', 'livree'])
        .order_by('-total_depense')[:10]
    )
    
    # Statistiques par méthode de paiement
    stats_paiement = (
        Paiement.objects
        .values('payment_method', 'payment_status')
        .annotate(count=Count('id'), total=Sum('amount'))
        .order_by('payment_method', 'payment_status')
    )
    
    # Évolution des ventes (30 derniers jours)
    ventes_journalieres = []
    for i in range(30):
        date = today - timedelta(days=i)
        ventes_jour = Commande.objects.filter(
            date_commande__date=date,
            statut='payee'
        ).aggregate(total=Sum('total'), nb=Count('id'))
        ventes_journalieres.append({
            'date': date.strftime('%d/%m/%Y'),
            'total': ventes_jour['total'] or 0,
            'nb_commandes': ventes_jour['nb'] or 0
        })
    
    ventes_journalieres.reverse()  # Plus récent en dernier
    
    context = {
        'total_commandes': total_commandes,
        'total_revenu': total_revenu,
        'commandes_en_attente': commandes_en_attente,
        'commandes_validees': commandes_validees,
        'commandes_livrees': commandes_livrees,
        
        'revenu_mois': revenu_mois,
        'nb_commandes_mois': nb_commandes_mois,
        'revenu_mois_precedent': revenu_mois_precedent,
        'nb_commandes_mois_precedent': nb_commandes_mois_precedent,
        
        'top_produits': top_produits,
        'top_clients': top_clients,
        'stats_paiement': stats_paiement,
        'ventes_journalieres': ventes_journalieres,
        
        'croissance_revenu': ((revenu_mois - revenu_mois_precedent) / revenu_mois_precedent * 100) if revenu_mois_precedent > 0 else 0,
        'croissance_commandes': ((nb_commandes_mois - nb_commandes_mois_precedent) / nb_commandes_mois_precedent * 100) if nb_commandes_mois_precedent > 0 else 0,
    }
    
    return render(request, 'admin/tableau_de_bord.html', context)