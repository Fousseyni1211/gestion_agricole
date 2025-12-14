from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from ..models.service import *

User = get_user_model()

class CategorieServiceForm(forms.ModelForm):
    class Meta:
        model = CategorieService
        fields = ['nom', 'description', 'icone', 'couleur', 'actif']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'couleur': forms.TextInput(attrs={'type': 'color'}),
        }
        help_texts = {
            'icone': "Entrez le nom de l'icône FontAwesome (ex: fa-cogs)",
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['nom', 'description', 'categorie', 'prix', 'duree_moyenne', 'statut', 'image', 'notes_internes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes_internes': forms.Textarea(attrs={'rows': 3}),
            'prix': forms.NumberInput(attrs={'step': '0.01'}),
            'duree_moyenne': forms.NumberInput(attrs={'min': '15', 'step': '15'}),
        }
        help_texts = {
            'duree_moyenne': 'Durée moyenne en minutes',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les catégories actives
        self.fields['categorie'].queryset = CategorieService.objects.filter(actif=True)
        
        # Personnalisation des champs
        self.fields['prix'].widget.attrs.update({'class': 'form-control', 'min': '0'})
        self.fields['duree_moyenne'].widget.attrs.update({'class': 'form-control'})

class DemandeServiceForm(forms.ModelForm):
    class Meta:
        model = DemandeService
        fields = ['service', 'description', 'statut', 'employe_attribue', 'notes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Décrivez votre demande en détail...'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Notes internes...'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les services actifs
        self.fields['service'].queryset = Service.objects.filter(statut='actif')
        
        # Filtrer les employés disponibles
        self.fields['employe_attribue'].queryset = User.objects.filter(
            role__in=['GERANT', 'EMPLOYE'], is_active=True
        )
        
        # Si l'utilisateur est un client, on ne lui permet pas de modifier le statut
        if user and user.role == 'CLIENT':
            if 'statut' in self.fields:
                del self.fields['statut']
            if 'employe_attribue' in self.fields:
                del self.fields['employe_attribue']
            if 'notes' in self.fields:
                self.fields['notes'].widget = forms.HiddenInput()

class InterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = ['description', 'duree', 'cout_materiel', 'cout_main_oeuvre', 'notes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Détails de l\'intervention...'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Notes supplémentaires...'}),
            'duree': forms.NumberInput(attrs={'min': '15', 'step': '15'}),
            'cout_materiel': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'cout_main_oeuvre': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
        help_texts = {
            'duree': 'Durée en minutes',
            'cout_materiel': 'Coût des matériaux utilisés',
            'cout_main_oeuvre': 'Coût de la main d\'œuvre',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['duree'].widget.attrs.update({'class': 'form-control'})
        self.fields['cout_materiel'].widget.attrs.update({'class': 'form-control'})
        self.fields['cout_main_oeuvre'].widget.attrs.update({'class': 'form-control'})

class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['client', 'date_emission', 'date_echeance', 'statut', 'tva', 'notes', 'mode_paiement', 'date_paiement', 'reference_paiement']
        widgets = {
            'date_emission': forms.DateInput(attrs={'type': 'date'}),
            'date_echeance': forms.DateInput(attrs={'type': 'date'}),
            'date_paiement': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
            'tva': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'}),
        }
        help_texts = {
            'tva': 'Taux de TVA en %',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = User.objects.filter(role='CLIENT', is_active=True)
        
        # Définir la date d'émission par défaut à aujourd'hui
        if not self.instance.pk:
            self.initial['date_emission'] = timezone.now().date()
            self.initial['date_echeance'] = timezone.now().date() + timezone.timedelta(days=30)
            self.initial['tva'] = 18.0  # TVA par défaut
    
    def clean(self):
        cleaned_data = super().clean()
        date_emission = cleaned_data.get('date_emission')
        date_echeance = cleaned_data.get('date_echeance')
        
        if date_emission and date_echeance and date_emission > date_echeance:
            raise ValidationError({
                'date_echeance': 'La date d\'échéance doit être postérieure à la date d\'émission.'
            })
        
        return cleaned_data

class LigneFactureServiceForm(forms.ModelForm):
    class Meta:
        model = LigneFactureService
        fields = ['demande_service', 'description', 'quantite', 'prix_unitaire', 'tva']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'tva': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        facture = kwargs.pop('facture', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les demandes de service non encore facturées pour ce client
        if facture and facture.client_id:
            self.fields['demande_service'].queryset = DemandeService.objects.filter(
                client=facture.client,
                ligne_facture__isnull=True  # Ne pas inclure les demandes déjà facturées
            )
        else:
            self.fields['demande_service'].queryset = DemandeService.objects.none()
        
        # Si une demande est sélectionnée, pré-remplir les champs
        if self.instance and self.instance.demande_service_id:
            self.initial['description'] = self.instance.demande_service.service.nom
            self.initial['prix_unitaire'] = self.instance.demande_service.service.prix
            self.initial['tva'] = 18.0  # TVA par défaut

# Formset pour les lignes de facture
LigneFactureServiceFormSet = inlineformset_factory(
    Facture, 
    LigneFactureService,
    form=LigneFactureServiceForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)
