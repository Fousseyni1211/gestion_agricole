# -*- coding: utf-8 -*-
from django.db import models
from django import forms
from .models import (
    CategorieDepense, CategorieRevenu, Depense, Revenu, 
    SoldeMensuel, Facture, PaiementClient, RapportFinancier, Client
)
from django.contrib.auth import get_user_model

User = get_user_model()

# ====== FORMULAIRES DE GESTION FINANCIÈRE ======

class CategorieDepenseForm(forms.ModelForm):
    class Meta:
        model = CategorieDepense
        fields = ['nom', 'description', 'couleur']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la catégorie'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description optionnelle'}),
            'couleur': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }

class CategorieRevenuForm(forms.ModelForm):
    class Meta:
        model = CategorieRevenu
        fields = ['nom', 'description', 'couleur']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la catégorie'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description optionnelle'}),
            'couleur': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }

class DepenseForm(forms.ModelForm):
    class Meta:
        model = Depense
        fields = ['categorie', 'titre', 'description', 'montant', 'date_depense', 
                 'fournisseur', 'numero_facture', 'piece_jointe', 'statut']
        widgets = {
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la dépense'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description détaillée'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'step': '0.01'}),
            'date_depense': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fournisseur': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du fournisseur'}),
            'numero_facture': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de facture'}),
            'piece_jointe': forms.FileInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

class RevenuForm(forms.ModelForm):
    class Meta:
        model = Revenu
        fields = ['categorie', 'titre', 'description', 'montant', 'date_revenu', 
                 'client', 'reference', 'piece_jointe', 'statut']
        widgets = {
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du revenu'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description détaillée'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'step': '0.01'}),
            'date_revenu': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'client': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Client ou source'}),
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Référence'}),
            'piece_jointe': forms.FileInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['numero_facture', 'client', 'date_emission', 'date_echeance', 
                 'montant_total', 'description']
        widgets = {
            'numero_facture': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de facture'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'date_emission': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_echeance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'montant_total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description des services/produits'}),
        }

class PaiementClientForm(forms.ModelForm):
    class Meta:
        model = PaiementClient
        fields = ['facture', 'montant', 'date_paiement', 'methode_paiement', 
                 'reference_paiement', 'notes', 'statut']
        widgets = {
            'facture': forms.Select(attrs={'class': 'form-select'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'step': '0.01'}),
            'date_paiement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'methode_paiement': forms.Select(attrs={'class': 'form-select'}),
            'reference_paiement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Référence du paiement'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes optionnelles'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

class RapportFinancierForm(forms.ModelForm):
    class Meta:
        model = RapportFinancier
        fields = ['type_rapport', 'titre', 'periode_debut', 'periode_fin']
        widgets = {
            'type_rapport': forms.Select(attrs={'class': 'form-select'}),
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du rapport'}),
            'periode_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'periode_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

# Formulaires de recherche et filtrage
class DepenseSearchForm(forms.Form):
    categorie = forms.ModelChoiceField(
        queryset=CategorieDepense.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    statut = forms.ChoiceField(
        choices=[('', 'Tous')] + Depense.STATUT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class RevenuSearchForm(forms.Form):
    categorie = forms.ModelChoiceField(
        queryset=CategorieRevenu.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    statut = forms.ChoiceField(
        choices=[('', 'Tous')] + Revenu.STATUT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class FactureSearchForm(forms.Form):
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    statut = forms.ChoicePERIOD_CHOICES .choices=[('',
        (' .choices=[('',  'TousPaiementClientForm(forms.ModelForm):
2
        model =  fields = [';        fields
        widgets = {
            'facture': forms.Select(attrs={'class': 'form-select'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'step': '0.01'}),
            'date_paiement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'methode_paiement': forms.Select(attrs={'class': 'form-select'}),
            'reference_paiement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Référence du paiement'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes optionnelles'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

class RapportFinancierForm(forms.ModelForm):
    class Meta:
        model = RapportFinancier
        fields = ['type_rapport', 'titre', 'periode_debut', 'periode_fin']
        widgets = {
            'type_rapport': forms.Select(attrs={'class': 'form-select'}),
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du rapport'}),
            'periode_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'periode_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

# Formulaires de recherche et filtrage
class DepenseSearchForm(forms.Form):
    categorie = forms.ModelChoiceField(
        queryset=CategorieDepense.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    statut = forms.ChoiceField(
        choices=[('', 'Tous')] + Depense.STATUT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class RevenuSearchForm(forms.Form):
    categorie = forms.ModelChoiceField(
        queryset=CategorieRevenu.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    statut = forms.ChoiceField(
        choices=[('', 'Tous')] + Revenu.STATUT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class FactureSearchForm(forms  .
       
        required=False)</form.choicess = [('Tous')] + Facture.STATUT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
