from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Culture
from .models import Culture, Meteo
from datetime import date
from .forms import CultureForm
from .forms import DepenseRevenuForm
from io import BytesIO
import openpyxl
from django.template.loader import get_template
from weasyprint import HTML
from .models import Culture, Commande, Paiement, Stock, Alerte, DepenseRevenu
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from .models import MouvementFinance
from django.db.models import Sum
def is_agriculteur(user):
    return user.role.lower() == 'agriculteur'

@user_passes_test(is_agriculteur)
@login_required
def agri_home(request):
    utilisateur = request.user

    # 1. Cultures
    cultures = Culture.objects.filter(utilisateur=utilisateur)

    # 2. Stocks faibles
    low_stocks = Stock.objects.filter(utilisateur=utilisateur, quantite__lt=10)

    # 3. Commandes récentes
    commandes = Commande.objects.filter(client=utilisateur).order_by('-date_commande')[:5]

    # 4. Paiements récents
    paiements = Paiement.objects.filter(commande__client=utilisateur).order_by('-payment_date')[:5]

    # 5. Alertes agricoles
    # alertes_conseils = Alerte.objects.filter(utilisateur=utilisateur).order_by('-date')[:5]

    # 6. Mouvements financiers récents
    mouvements_recents = DepenseRevenu.objects.filter(agriculteur=utilisateur).order_by('-date')[:7]

    # 7. Filtres par mois
    selected_month = request.GET.get('mois')
    if selected_month:
        mois = datetime.strptime(selected_month, '%Y-%m')
        mouvements = DepenseRevenu.objects.filter(
            agriculteur=utilisateur,
            date__year=mois.year,
            date__month=mois.month
        )
    else:
        mouvements = DepenseRevenu.objects.filter(agriculteur=utilisateur)

    # 8. Totaux par type
    total_depenses = mouvements.filter(type='depense').aggregate(Sum('montant'))['montant__sum'] or 0
    total_revenus = mouvements.filter(type='revenu').aggregate(Sum('montant'))['montant__sum'] or 0
    solde = total_revenus - total_depenses

    # 9. Mois disponibles pour dropdown
    mois_disponibles = DepenseRevenu.objects.filter(agriculteur=utilisateur) \
        .dates('date', 'month', order='DESC')

    context = {
        'cultures': cultures,
        'low_stocks': low_stocks,
        'commandes': commandes,
        'derniers_paiements': paiements,
        # 'alertes_conseils': alertes_conseils,
        'mouvements_recents': mouvements_recents,
        'total_depenses': total_depenses,
        'total_revenus': total_revenus,
        'solde': solde,
        'mouvements': mouvements,
        'mois_disponibles': mois_disponibles,
        'selected_month': selected_month or '',
    }
    return render(request, 'agriculteur/agri_home.html', context)
@user_passes_test(is_agriculteur)
def liste_cultures(request):
    cultures = Culture.objects.filter(utilisateur=request.user).order_by("-date_semis")
    return render(request, "agriculteur/liste_cultures.html", {"cultures": cultures})

@login_required
def ajouter_culture(request):
    if request.method == 'POST':
        form = CultureForm(request.POST)
        if form.is_valid():
            culture = form.save(commit=False)
            culture.utilisateur = request.user
            culture.save()
            return redirect('liste_cultures')  # nom de l'URL
    else:
        form = CultureForm()
    return render(request, 'agriculteur/ajouter_culture.html', {'form': form})
@login_required
@user_passes_test(is_agriculteur)
def detail_culture(request, culture_id):
    culture = get_object_or_404(Culture, id=culture_id)

    meteo = None
    if culture.localisation:
        try:
            api_key = 'ta_clé_api_openweathermap'
            ville = culture.localisation
            url = f'https://api.openweathermap.org/data/2.5/weather?q={ville}&appid={api_key}&units=metric&lang=fr'
            response = requests.get(url)
            data = response.json()

            if data.get('main'):
                meteo = {
                    'temperature': data['main']['temp'],
                    'condition': data['weather'][0]['description'].capitalize(),
                    'humidite': data['main']['humidity'],
                    'vent': data['wind']['speed']
                }
        except Exception as e:
            print("Erreur météo :", e)

    return render(request, 'agriculteur/detail_culture.html', {
        'culture': culture,
        'meteo': meteo
    })
@user_passes_test(is_agriculteur)
def liste_transactions(request):
    transactions = Transaction.objects.filter(utilisateur=request.user).order_by("-date")
    total_revenus = sum(t.montant for t in transactions if t.type_transaction == "revenu")
    total_depenses = sum(t.montant for t in transactions if t.type_transaction == "depense")
    solde = total_revenus - total_depenses
    return render(
        request,
        "transactions/liste.html",
        {
            "transactions": transactions,
            "total_revenus": total_revenus,
            "total_depenses": total_depenses,
            "solde": solde,
        },
    )

@login_required
@user_passes_test(is_agriculteur)
def ajouter_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.utilisateur = request.user
            transaction.save()
            return redirect("liste_transactions")
    else:
        form = TransactionForm()
    return render(request, "agriculteur/ajouter.html", {"form": form})
@login_required
def profil_modifier(request):
    return render(request, 'agriculteur/modifier_profil.html')

@login_required
def liste_finances(request):
    mouvements = DepenseRevenu.objects.filter(agriculteur=request.user).order_by('-date')

    total_depenses = mouvements.filter(type='DEPENSE').aggregate(total=Sum('montant'))['total'] or 0
    total_revenus = mouvements.filter(type='REVENU').aggregate(total=Sum('montant'))['total'] or 0
    profit = total_revenus - total_depenses

    context = {
        'mouvements': mouvements,
        'total_depenses': total_depenses,
        'total_revenus': total_revenus,
        'profit': profit,
    }
    return render(request, 'agriculteur/finances.html', context)

@login_required
def ajouter_mouvement(request):
    if request.method == 'POST':
        form = DepenseRevenuForm(request.POST)
        if form.is_valid():
            mouvement = form.save(commit=False)
            mouvement.agriculteur = request.user

            # Calcul automatique montant si quantite et prix unitaire renseignés (ex: vente récolte)
            if mouvement.quantite and mouvement.prix_unitaire:
                mouvement.montant = mouvement.quantite * mouvement.prix_unitaire

            mouvement.save()
            return redirect('liste_finances')
    else:
        form = DepenseRevenuForm()
    return render(request, 'agriculteur/ajouter_mouvement.html', {'form': form})
@login_required
def mouvements_recap(request):
    utilisateur = request.user
    mois = request.GET.get('mois')
    
    mouvements = DepenseRevenu.objects.filter(utilisateur=utilisateur)
    if mois:
        mouvements = mouvements.filter(date__month=mois)
    
    total_revenus = mouvements.filter(type='revenu').aggregate(Sum('montant'))['montant__sum'] or 0
    total_depenses = mouvements.filter(type='depense').aggregate(Sum('montant'))['montant__sum'] or 0
    
    context = {
        'mouvements': mouvements.order_by('-date'),
        'total_revenus': total_revenus,
        'total_depenses': total_depenses,
        'mois_actuel': mois or now().month
    }
    return render(request, 'agriculteur/mouvements_recap.html', context)
@login_required
def export_mouvements_pdf(request):
    utilisateur = request.user
    mouvements = DepenseRevenu.objects.filter(utilisateur=utilisateur).order_by('-date')
    template = get_template('agriculteur/pdf_mouvements.html')
    html = template.render({'mouvements': mouvements})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mouvements.pdf"'

    pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)
    return response
@login_required
def export_excel_mouvements(request):
    utilisateur = request.user
    mouvements = DepenseRevenu.objects.filter(utilisateur=utilisateur).order_by('-date')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Mouvements"

    ws.append(['Date', 'Description', 'Type', 'Montant'])

    for m in mouvements:
        ws.append([m.date.strftime('%Y-%m-%d'), m.description, m.type, float(m.montant)])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="mouvements.xlsx"'
    wb.save(response)
    return response
@login_required
def export_resume_pdf(request):
    user = request.user
    mois = request.GET.get("mois", datetime.datetime.now().month)
    annee = datetime.datetime.now().year

    mouvements = DepenseRevenu.objects.filter(
        utilisateur=user,
        date__month=mois,
        date__year=annee
    )

    total_revenus = sum(m.montant for m in mouvements if m.type == 'revenu')
    total_depenses = sum(m.montant for m in mouvements if m.type == 'depense')
    solde = total_revenus - total_depenses

    mois_nom = datetime.date(1900, int(mois), 1).strftime('%B')

    context = {
        "mois_nom": mois_nom.capitalize(),
        "annee": annee,
        "total_revenus": total_revenus,
        "total_depenses": total_depenses,
        "solde": solde,
        "date_now": datetime.datetime.now().strftime("%d/%m/%Y"),
        "logo_url": request.build_absolute_uri('/static/img/logo.png'),
    }

    html = render_to_string("pdf_resume_mois.html", context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Resume_{mois_nom}_{annee}.pdf"'
    pisa.CreatePDF(BytesIO(html.encode("utf-8")), dest=response)
    return response
@login_required
def export_pdf_mouvements(request):
    utilisateur = request.user
    mouvements = DepenseRevenu.objects.filter(utilisateur=utilisateur).order_by('-date')

    # Rendre le template en HTML string
    html_string = render_to_string('pdf_mouvements.html', {'mouvements': mouvements, 'utilisateur': utilisateur})

    # Générer PDF à partir de la string HTML
    pdf_file = HTML(string=html_string).write_pdf()

    # Préparer la réponse HTTP avec le PDF en pièce jointe
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mouvements_financiers.pdf"'

    return response
@login_required
def reserver_materiel(request, materiel_id):
    materiel = get_object_or_404(Materiel, id=materiel_id)

    if request.method == 'POST':
        date_debut_str = request.POST.get('date_debut')
        date_fin_str = request.POST.get('date_fin')
        commentaire = request.POST.get('commentaire', '').strip()

        # Conversion des dates
        try:
            date_debut = datetime.datetime.strptime(date_debut_str, '%Y-%m-%d').date()
            date_fin = datetime.datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, "Format de date invalide.")
            return render(request, 'reserver_materiel.html', {
                'materiel': materiel,
                'today': datetime.date.today().isoformat(),
            })

        today = datetime.date.today()

        # Validation dates
        if date_debut < today or date_fin < today:
            messages.error(request, "Les dates doivent être égales ou supérieures à aujourd'hui.")
        elif date_fin < date_debut:
            messages.error(request, "La date de fin doit être supérieure ou égale à la date de début.")
        else:
            # Vérifier disponibilité : Pas de réservation validée qui chevauche ces dates
            conflits = ReservationMateriel.objects.filter(
                materiel=materiel,
                validee=True,
                date_fin__gte=date_debut,
                date_debut__lte=date_fin
            )
            if conflits.exists():
                messages.error(request, "Ce matériel est déjà réservé pour ces dates.")
            else:
                # Créer la réservation (non validée par défaut)
                reservation = ReservationMateriel.objects.create(
                    materiel=materiel,
                    client=request.user,
                    date_debut=date_debut,
                    date_fin=date_fin,
                    commentaire=commentaire,
                    validee=False
                )

                # Notification admin (par email)
                admin_email = settings.ADMIN_EMAIL  # Assure-toi de définir cette variable dans settings.py
                subject = f"Nouvelle demande de réservation - {materiel.nom}"
                message = (
                    f"L'utilisateur {request.user.username} a demandé une réservation pour le matériel : {materiel.nom}\n"
                    f"Période : {date_debut} au {date_fin}\n"
                    f"Commentaire : {commentaire}\n\n"
                    "Merci de valider cette réservation dans l'administration."
                )
                if admin_email:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin_email])

                messages.success(request, "Votre demande de réservation a été envoyée avec succès. Vous serez informé après validation.")
                return redirect('location_materiel')  # Remplace par ta vue liste/location

    else:
        today = datetime.date.today()

    return render(request, 'reserver_materiel.html', {
        'materiel': materiel,
        'today': today.isoformat(),
    })
def liste_materiels(request):
    materiels = Materiel.objects.all()
    disponibilite = request.GET.get('disponibilite')
    categorie = request.GET.get('categorie')

    if disponibilite:
        materiels = materiels.filter(disponible=(disponibilite == 'oui'))

    if categorie:
        materiels = materiels.filter(categorie=categorie)

    categories = Materiel.objects.values_list('categorie', flat=True).distinct()

    return render(request, 'location/liste_materiels.html', {
        'materiels': materiels,
        'categories': categories,
    })
def boutique_bio(request):
    # Exemple : liste de produits bio fictifs
    produits = [
        {'nom': 'Tomates Bio', 'description': 'Tomates fraîches et bio', 'prix': 2.50},
        {'nom': 'Miel Naturel', 'description': 'Miel pur et local', 'prix': 5.00},
        {'nom': 'Farine Complète', 'description': 'Farine bio moulue sur meule', 'prix': 3.20},
    ]
    context = {
        'produits': produits,
    }
    return render(request, 'agriculteur/boutique_bio.html', context)