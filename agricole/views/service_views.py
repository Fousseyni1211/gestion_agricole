from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
import os
from datetime import timedelta

from ..models.service import *
from ..models import CustomUser
from ..forms import *

def is_gerant(user):
    return user.is_authenticated and user.role == 'GERANT'

class GerantRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_gerant(self.request.user)

# Vues pour les catégories de services
class CategorieServiceListView(LoginRequiredMixin, GerantRequiredMixin, ListView):
    model = CategorieService
    template_name = 'admin/service/categorie_list.html'
    context_object_name = 'categories'
    paginate_by = 10

class CategorieServiceCreateView(LoginRequiredMixin, GerantRequiredMixin, CreateView):
    model = CategorieService
    form_class = CategorieServiceForm
    template_name = 'admin/service/categorie_form.html'
    success_url = reverse_lazy('liste_categories_service')
    
    def form_valid(self, form):
        messages.success(self.request, 'Catégorie créée avec succès.')
        return super().form_valid(form)

class CategorieServiceUpdateView(LoginRequiredMixin, GerantRequiredMixin, UpdateView):
    model = CategorieService
    form_class = CategorieServiceForm
    template_name = 'admin/service/categorie_form.html'
    success_url = reverse_lazy('liste_categories_service')
    
    def form_valid(self, form):
        messages.success(self.request, 'Catégorie mise à jour avec succès.')
        return super().form_valid(form)

@login_required
@user_passes_test(is_gerant)
def toggle_categorie_status(request, pk):
    categorie = get_object_or_404(CategorieService, pk=pk)
    categorie.actif = not categorie.actif
    categorie.save()
    status = "activée" if categorie.actif else "désactivée"
    messages.success(request, f'Catégorie {status} avec succès.')
    return redirect('liste_categories_service')

# Vues pour les services
class ServiceListView(LoginRequiredMixin, GerantRequiredMixin, ListView):
    model = Service
    template_name = 'admin/service/service_list.html'
    context_object_name = 'services'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('categorie')
        search = self.request.GET.get('search')
        categorie = self.request.GET.get('categorie')
        statut = self.request.GET.get('statut')
        
        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) | 
                Q(description__icontains=search) |
                Q(categorie__nom__icontains=search)
            )
        if categorie:
            queryset = queryset.filter(categorie_id=categorie)
        if statut:
            queryset = queryset.filter(statut=statut)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategorieService.objects.filter(actif=True)
        context['search'] = self.request.GET.get('search', '')
        context['selected_categorie'] = self.request.GET.get('categorie', '')
        context['selected_statut'] = self.request.GET.get('statut', '')
        return context

class ServiceCreateView(LoginRequiredMixin, GerantRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'admin/service/service_form.html'
    success_url = reverse_lazy('liste_services')
    
    def form_valid(self, form):
        messages.success(self.request, 'Service créé avec succès.')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class ServiceUpdateView(LoginRequiredMixin, GerantRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'admin/service/service_form.html'
    success_url = reverse_lazy('liste_services')
    
    def form_valid(self, form):
        messages.success(self.request, 'Service mis à jour avec succès.')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

@login_required
@user_passes_test(is_gerant)
def service_detail(request, pk):
    service = get_object_or_404(Service.objects.select_related('categorie'), pk=pk)
    return render(request, 'admin/service/service_detail.html', {'service': service})

# Vues pour les demandes de service
class DemandeServiceListView(LoginRequiredMixin, GerantRequiredMixin, ListView):
    model = DemandeService
    template_name = 'admin/service/demande_list.html'
    context_object_name = 'demandes'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('client', 'service', 'employe_attribue')
        
        # Filtres
        statut = self.request.GET.get('statut')
        client = self.request.GET.get('client')
        date_debut = self.request.GET.get('date_debut')
        date_fin = self.request.GET.get('date_fin')
        
        if statut:
            queryset = queryset.filter(statut=statut)
        if client:
            queryset = queryset.filter(client_id=client)
        if date_debut and date_fin:
            queryset = queryset.filter(
                date_demande__date__range=[date_debut, date_fin]
            )
            
        return queryset.order_by('-date_demande')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = CustomUser.objects.filter(role='CLIENT')
        context['statuts'] = DemandeService.StatutDemande.choices
        context['selected_statut'] = self.request.GET.get('statut', '')
        context['selected_client'] = self.request.GET.get('client', '')
        context['date_debut'] = self.request.GET.get('date_debut', '')
        context['date_fin'] = self.request.GET.get('date_fin', '')
        
        # Statistiques
        context['total_demandes'] = self.get_queryset().count()
        context['demandes_nouvelles'] = self.get_queryset().filter(statut='nouvelle').count()
        context['demandes_en_cours'] = self.get_queryset().filter(statut='en_cours').count()
        context['demandes_terminees'] = self.get_queryset().filter(statut='terminee').count()
        
        return context

class DemandeServiceDetailView(LoginRequiredMixin, GerantRequiredMixin, DetailView):
    model = DemandeService
    template_name = 'admin/service/demande_detail.html'
    context_object_name = 'demande'
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'client', 'service', 'employe_attribue', 'facture'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employes'] = CustomUser.objects.filter(
            role__in=['GERANT', 'EMPLOYE']
        )
        context['interventions'] = self.object.interventions.select_related('technicien').order_by('-date_intervention')
        return context

@login_required
@user_passes_test(is_gerant)
def changer_statut_demande(request, pk, statut):
    demande = get_object_or_404(DemandeService, pk=pk)
    statuts = dict(DemandeService.StatutDemande.choices)
    
    if statut not in statuts:
        messages.error(request, 'Statut invalide.')
        return redirect('detail_demande_service', pk=pk)
    
    demande.statut = statut
    
    # Mettre à jour les dates en fonction du statut
    if statut == 'en_cours' and not demande.date_prise_en_charge:
        demande.date_prise_en_charge = timezone.now()
    elif statut == 'terminee' and not demande.date_fin:
        demande.date_fin = timezone.now()
    
    demande.save()
    
    messages.success(request, f'Statut de la demande mis à jour: {statuts[statut]}')
    return redirect('detail_demande_service', pk=pk)

@login_required
@user_passes_test(is_gerant)
def attribuer_employe(request, pk):
    if request.method == 'POST':
        demande = get_object_or_404(DemandeService, pk=pk)
        employe_id = request.POST.get('employe_id')
        
        if employe_id:
            employe = get_object_or_404(CustomUser, pk=employe_id, role__in=['GERANT', 'EMPLOYE'])
            demande.employe_attribue = employe
            
            # Si c'est la première attribution, marquer comme en cours
            if demande.statut == 'nouvelle':
                demande.statut = 'en_cours'
                demande.date_prise_en_charge = timezone.now()
            
            demande.save()
            messages.success(request, f'Employé {employe.get_full_name()} attribué avec succès.')
        else:
            messages.error(request, 'Veuillez sélectionner un employé.')
    
    return redirect('detail_demande_service', pk=pk)

# Vues pour les interventions
@login_required
@user_passes_test(is_gerant)
class InterventionCreateView(LoginRequiredMixin, GerantRequiredMixin, CreateView):
    model = Intervention
    form_class = InterventionForm
    template_name = 'admin/service/intervention_form.html'
    
    def get_success_url(self):
        return reverse_lazy('detail_demande_service', kwargs={'pk': self.kwargs['demande_pk']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['demande'] = get_object_or_404(DemandeService, pk=self.kwargs['demande_pk'])
        return context
    
    def form_valid(self, form):
        form.instance.demande_id = self.kwargs['demande_pk']
        form.instance.technicien = self.request.user
        messages.success(self.request, 'Intervention enregistrée avec succès.')
        return super().form_valid(form)

# Vues pour les factures
class FactureListView(LoginRequiredMixin, GerantRequiredMixin, ListView):
    model = Facture
    template_name = 'admin/service/facture_list.html'
    context_object_name = 'factures'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('client')
        
        # Filtres
        statut = self.request.GET.get('statut')
        client = self.request.GET.get('client')
        date_debut = self.request.GET.get('date_debut')
        date_fin = self.request.GET.get('date_fin')
        
        if statut:
            queryset = queryset.filter(statut=statut)
        if client:
            queryset = queryset.filter(client_id=client)
        if date_debut and date_fin:
            queryset = queryset.filter(
                date_emission__range=[date_debut, date_fin]
            )
            
        return queryset.order_by('-date_emission', '-numero')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = CustomUser.objects.filter(role='CLIENT')
        context['statuts'] = Facture.StatutFacture.choices
        context['selected_statut'] = self.request.GET.get('statut', '')
        context['selected_client'] = self.request.GET.get('client', '')
        context['date_debut'] = self.request.GET.get('date_debut', '')
        context['date_fin'] = self.request.GET.get('date_fin', '')
        
        # Statistiques
        context['total_factures'] = self.get_queryset().count()
        context['montant_total'] = self.get_queryset().aggregate(Sum('montant_ttc'))['montant_ttc__sum'] or 0
        context['factures_impayees'] = self.get_queryset().exclude(statut='payee').count()
        
        return context

class FactureDetailView(LoginRequiredMixin, GerantRequiredMixin, DetailView):
    model = Facture
    template_name = 'admin/service/facture_detail.html'
    context_object_name = 'facture'
    
    def get_queryset(self):
        return super().get_queryset().select_related('client', 'cree_par')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lignes'] = self.object.lignes.select_related('demande_service')
        return context

@login_required
@user_passes_test(is_gerant)
def generer_facture_pdf(request, pk):
    facture = get_object_or_404(Facture.objects.select_related('client'), pk=pk)
    lignes = facture.lignes.select_related('demande_service')
    
    context = {
        'facture': facture,
        'lignes': lignes,
        'date_emission': timezone.now().date(),
        'echeance': (timezone.now() + timedelta(days=30)).date(),
    }
    
    # Rendu du template HTML en PDF
    html_string = render_to_string('admin/service/facture_pdf.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    
    # Création du PDF
    pdf_file = html.write_pdf()
    
    # Réponse avec le PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{facture.numero}.pdf"'
    return response

# Tableau de bord
@login_required
@user_passes_test(is_gerant)
def dashboard_service(request):
    # Statistiques générales
    stats = {
        'total_services': Service.objects.count(),
        'total_demandes': DemandeService.objects.count(),
        'demandes_nouvelles': DemandeService.objects.filter(statut='nouvelle').count(),
        'demandes_en_cours': DemandeService.objects.filter(statut='en_cours').count(),
        'chiffre_affaires': Facture.objects.filter(statut='payee').aggregate(Sum('montant_ttc'))['montant_ttc__sum'] or 0,
    }
    
    # Dernières demandes
    dernieres_demandes = DemandeService.objects.select_related('client', 'service').order_by('-date_demande')[:5]
    
    # Dernières factures
    dernieres_factures = Facture.objects.select_related('client').order_by('-date_emission')[:5]
    
    # Services les plus demandés
    services_populaires = Service.objects.annotate(
        nb_demandes=Count('demandes')
    ).filter(nb_demandes__gt=0).order_by('-nb_demandes')[:5]
    
    context = {
        'stats': stats,
        'dernieres_demandes': dernieres_demandes,
        'dernieres_factures': dernieres_factures,
        'services_populaires': services_populaires,
    }
    
    return render(request, 'admin/service/dashboard.html', context)

# API pour les statistiques (utilisées dans les graphiques)
@login_required
@user_passes_test(is_gerant)
def api_statistiques(request):
    # Statistiques par statut de demande
    stats_demandes = DemandeService.objects.values('statut').annotate(
        total=Count('id')
    ).order_by('statut')
    
    # Chiffre d'affaires par mois
    ca_par_mois = Facture.objects.filter(
        date_emission__year=timezone.now().year
    ).values('date_emission__month').annotate(
        mois=Count('date_emission__month'),
        total=Sum('montant_ttc')
    ).order_by('date_emission__month')
    
    # Préparation des données pour les graphiques
    data = {
        'labels': [dict(DemandeService.StatutDemande.choices).get(stat['statut'], stat['statut']) 
                  for stat in stats_demandes],
        'data': [stat['total'] for stat in stats_demandes],
        'mois': [f"{stat['date_emission__month']:02d}/{timezone.now().year}" for stat in ca_par_mois],
        'ca': [float(stat['total'] or 0) for stat in ca_par_mois],
    }
    
    return JsonResponse(data)

# Vues pour l'API (utilisées en AJAX)
@login_required
@require_http_methods(["GET"])
def api_services(request):
    query = request.GET.get('q', '')
    
    services = Service.objects.filter(
        Q(nom__icontains=query) |
        Q(description__icontains=query)
    ).values('id', 'nom', 'prizo', 'description')
    
    return JsonResponse(list(services), safe=False)

@login_required
@require_http_methods(["POST"])
def api_creer_demande(request):
    if request.method == 'POST':
        form = DemandeServiceForm(request.POST, user=request.user)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.client = request.user
            demande.save()
            return JsonResponse({'success': True, 'id': demande.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
