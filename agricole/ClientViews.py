from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib import messages
from django.template.loader import get_template
from django.http import HttpResponse
from datetime import datetime
import requests
from weasyprint import HTML
import os
from django.conf import settings
from django.contrib.staticfiles import finders
from .models import Notification
from .forms import CommandeForm, DetailCommandeFormSet
from django.forms import inlineformset_factory
from .models import Commande, DetailCommande, Produit
from .forms import CommandeForm, DetailCommandeForm

from .models import (
    Commande, Paiement, DepenseRevenu, ReservationMateriel,
    Alerte, Culture, Stock, Materiel
)

@login_required
def location_materiel(request):
    materiels = Materiel.objects.all()
    return render(request, 'client/location_materiel.html', {'materiels': materiels})

@login_required
def client_home(request):
    client = request.user
    user = request.user

    # 1. Statistiques
    nb_commandes = Commande.objects.filter(client=client).count()
    total_paiements = Paiement.objects.filter(commande__client=user).aggregate(Sum('amount'))['amount__sum'] or 0
    nb_reservations = ReservationMateriel.objects.filter(client=client).count()

    # 2. Derniers paiements
    derniers_paiements = Paiement.objects.filter(commande__client=client).order_by('-payment_date')[:5]

    # 3. Dernières commandes
    commandes_recents = Commande.objects.filter(client=client).order_by('-date_commande')[:5]

    # 4. Derniers mouvements financiers
    mouvements = DepenseRevenu.objects.filter(agriculteur=client).order_by('-date')[:5]

    # 5. Alertes et conseils
    alertes = Alerte.objects.filter(client=user).order_by('-date')[:5]

    # 6. Prévisions météo
    try:
        ville = "Bamako"
        api_key = "c02d9fe1xxxxxxxxxxxxx23ed0"  # Remplace avec ta clé OpenWeather
        
        # Données météo fictives pour la démo
        meteo = {
            'ville': 'Bamako',
            'temperature': 28,
            'description': 'Ensoleillé',
            'humidite': 65,
            'vent': 12
        }
    except Exception as e:
        meteo = {
            'ville': 'Bamako',
            'temperature': '--',
            'description': 'Données non disponibles',
            'humidite': '--',
            'vent': '--'
        }

    # 7. Solde courant (revenus - dépenses)
    total_depenses = DepenseRevenu.objects.filter(agriculteur=client, type='DEPENSE').aggregate(Sum('montant'))['montant__sum'] or 0
    total_revenus = DepenseRevenu.objects.filter(agriculteur=client, type='REVENU').aggregate(Sum('montant'))['montant__sum'] or 0
    solde = total_revenus - total_depenses

    context = {
        'nb_commandes': nb_commandes,
        'total_paiements': total_paiements,
        'nb_reservations': nb_reservations,
        'derniers_paiements': derniers_paiements,
        'commandes_recents': commandes_recents,
        'mouvements': mouvements,
        'alertes': alertes,
        'meteo': meteo,
        'total_depenses': total_depenses,
        'total_revenus': total_revenus,
        'solde': solde,
        'mois_actuel': datetime.now().strftime("%B %Y")
    }
    return render(request, 'client/client_home.html', context)
@login_required
def mes_commandes(request):
    commandes = Commande.objects.filter(client=request.user).prefetch_related('details__produit').order_by('-date_commande')
    return render(request, 'commande/mes_commandes.html', {'commandes': commandes})

@login_required
def historique_paiements(request):
    paiements = Paiement.objects.filter(commande__client=request.user).order_by('-payment_date')
    total = paiements.aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'client/historique_paiements.html', {
        'paiements': paiements,
        'total': total
    })

@login_required
def factures_client(request):
    factures = Paiement.objects.filter(commande__client=request.user)
    return render(request, 'client/factures_client.html', {'factures': factures})
@login_required
def mes_reservations(request):
    reservations = ReservationMateriel.objects.filter(client=request.user)
    return render(request, 'client/mes_reservations.html', {'reservations': reservations})
@login_required
def mes_alertes(request):
    alertes = Alerte.objects.filter(client=request.user)
    return render(request, 'client/mes_alertes.html', {'alertes': alertes})
@login_required
def finance_client(request):
    mouvements = DepenseRevenu.objects.filter(agriculteur=request.user).order_by('-date')
    return render(request, 'client/finance_client.html', {'mouvements': mouvements})
@login_required
def culture_client(request):
    cultures = Culture.objects.filter(utilisateur=request.user)
    return render(request, 'client/mes_cultures.html', {'cultures': cultures})
def boutique_bio(request):
    produits = Produit.objects.filter(type_produit__icontains='bio')
    return render(request, 'client/boutique_bio.html', {'produits': produits})

def conseil_agricole(request):
    """
    Vue pour la page de conseil agricole.
    Pour l'instant, c'est une page de démonstration.
    """
    return render(request, 'client/conseil_agricole.html')

@login_required
def alertes_client(request):
    alertes = Alerte.objects.filter(client=request.user).order_by('-date')  # ou 'utilisateur' selon ton modèle
    return render(request, 'client/alertes_client.html', {'alertes': alertes})
@login_required
def recap_financier_client(request):
    mouvements = DepenseRevenu.objects.filter(agriculteur=request.user).order_by('-date')
    solde = mouvements.aggregate(Sum('montant'))['montant__sum'] or 0

    return render(request, 'client/recap_financier.html', {
        'mouvements': mouvements,
        'solde': solde,
    })
@login_required
def meteo_client(request):
    ville = "Bamako"
    api_key = "c02d9fe1xxxxxxxxxxxxx23ed0"  # Remplace avec ta clé OpenWeather
    
    # Données météo fictives pour la démo
    meteo_data = [
        {
            "date": "2025-08-12",
            "temperature": 28,
            "humidite": 65,
            "pluie": "Ensoleillé"
        },
        {
            "date": "2025-08-13",
            "temperature": 30,
            "humidite": 70,
            "pluie": "Partiellement nuageux"
        },
        {
            "date": "2025-08-14",
            "temperature": 27,
            "humidite": 75,
            "pluie": "Pluie légère"
        },
        {
            "date": "2025-08-15",
            "temperature": 29,
            "humidite": 60,
            "pluie": "Ensoleillé"
        }
    ]
    
    # Essayer de récupérer les données réelles si possible
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={ville}&appid={api_key}&units=metric&lang=fr"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            meteo_data = []
            for i in range(0, 32, 8):  # 4 jours = toutes les 24h
                if i < len(data['list']):
                    item = data['list'][i]
                    meteo_data.append({
                        "date": item['dt_txt'].split(" ")[0],
                        "temperature": int(item['main']['temp']),
                        "humidite": item['main']['humidity'],
                        "pluie": item.get('weather', [{}])[0].get('description', 'N/A').capitalize()
                    })
    except Exception as e:
        # En cas d'erreur, on garde les données fictives
        pass

    return render(request, 'client/meteo_client.html', {"meteo_data": meteo_data})
@login_required
def avis_client(request):
    return render(request, 'client/avis_client.html')

@login_required
def profil_client(request):
    user = request.user
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        # Mettre à jour les informations de l'utilisateur
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone = phone
        user.address = address
        user.save()
        
        messages.success(request, "Votre profil a été mis à jour avec succès.")
        return redirect('profil_client')
    
    context = {
        'user': user
    }
    return render(request, 'client/profil_client.html', context)

@login_required
def parametres_client(request):
    """
    Vue pour la page des paramètres du client.
    """
    if request.method == 'POST':
        # Handle form submission
        messages.success(request, 'Vos paramètres ont été mis à jour avec succès.')
        return redirect('parametres_client')
    
    context = {
        'user': request.user,
        'notifications': Notification.objects.filter(user=request.user, read=False).order_by('-created_at')[:5],
        'unread_count': Notification.objects.filter(user=request.user, read=False).count()
    }
    return render(request, 'client/parametres_client.html', context)

DetailCommandeFormSet = inlineformset_factory(
    Commande, DetailCommande, form=DetailCommandeForm, extra=1, can_delete=False
)

@login_required
def passer_commande(request):
    if request.method == 'POST':
        commande_form = CommandeForm(request.POST)
        formset = DetailCommandeFormSet(request.POST)
        if commande_form.is_valid() and formset.is_valid():
            commande = commande_form.save(commit=False)
            commande.client = request.user
            commande.save()
            details = formset.save(commit=False)
            for detail in details:
                detail.commande = commande
                produit = detail.produit
                if detail.quantite > produit.stock:
                    formset.add_error(None, f"Stock insuffisant pour {produit.nom}")
                    return render(request, 'commande/passer_commande.html', {
                        'commande_form': commande_form, 'formset': formset
                    })
                produit.stock -= detail.quantite
                produit.save()
                detail.save()
            return redirect('mes_commandes')
    else:
        commande_form = CommandeForm()
        formset = DetailCommandeFormSet()
    return render(request, 'commande/passer_commande.html', {
        'commande_form': commande_form, 'formset': formset
    })

@login_required
def mes_commandes(request):
    commandes = Commande.objects.filter(client=request.user).prefetch_related('details__produit').order_by('-date_commande')
    return render(request, 'commande/mes_commandes.html', {'commandes': commandes})

# Validation par admin
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def valider_commande(request, commande_id):
    commande = get_object_or_404(Commande, pk=commande_id)
    commande.statut = 'validee'
    commande.save()
    return redirect('liste_commandes_admin')
# ➜ Détail d'une commande
@login_required
def detail_commande(request, commande_id):
    commande = get_object_or_404(
        Commande.objects.prefetch_related('details__produit'),
        id=commande_id, client=request.user
    )
    return render(request, 'commandes/detail_commande.html', {'commande': commande})

@login_required
def supprimer_commande(request, commande_id):
    commande = get_object_or_404(Commande, pk=commande_id, client=request.user)
    if request.method == 'POST':
        commande.delete()
        messages.success(request, "Commande supprimée.")
        return redirect('mes_commandes')
    return render(request, 'client/confirm_delete.html', {'commande': commande})

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path

@login_required
def export_pdf_commande(request, commande_id):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from django.http import HttpResponse

    # 🔹 Réponse PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="commande_{commande_id}.pdf"'

    # 🔹 Fichier PDF en mémoire
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    # ✅ Corriger le chemin du logo
    logo_path = os.path.join(settings.STATICFILES_DIRS[0], "images", "logo.vif")
    if os.path.exists(logo_path):
        img = Image(logo_path, width=100, height=50)
        elements.append(img)
        elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Facture Commande n° {commande_id}", styles["Title"]))

    # 🔹 Génération
    doc.build(elements)

    return response
@login_required
def client_notifications(request):
    """Affiche les notifications pour le client."""
    # Récupérer les notifications du client
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'client/notifications.html', {
        'notifications': notifications
    })

@login_required
def marquer_notification_lue(request, notification_id):
    """Marque une notification comme lue."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()  # Ou vous pourriez ajouter un champ 'lue' et le mettre à True
    return redirect('client_notifications')

@login_required
def api_detail_commande(request, commande_id):
    commande = get_object_or_404(Commande, pk=commande_id, client=request.user)
    details = commande.details.all()
    
    details_data = [
        {
            'produit': detail.produit.nom_produit,
            'quantite': detail.quantite,
            'prix_unitaire': detail.prix_unitaire,
            'sous_total': detail.sous_total
        }
        for detail in details
    ]
    
    data = {
        'id': commande.id,
        'date': commande.date_commande.strftime('%d/%m/%Y %H:%M'),
        'statut': commande.get_statut_display(),
        'total': commande.total,
        'details': details_data
    }
    
    return JsonResponse(data)