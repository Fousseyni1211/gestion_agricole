from django import forms
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import MouvementStock, Parcelle, ItineraireTechnique, ActiviteAgricole
from .models import Produit, Commande, CustomUser, Culture, Agriculteur
from .models import Commande, LigneCommande
from .models import Commande, Client
from .models import FicheConseil, PhotoCulture
from django.forms import inlineformset_factory
from django.contrib.auth import get_user_model
from django.forms import modelformset_factory
from .models import Culture
from .models import Stock
from django.forms import formset_factory

from .models import Transaction
from .models import DetailCommande
from .models import DepenseRevenu, Produit
# Champ personnalisé pour la date
class DateInput(forms.DateInput):
    input_type = "date"

# Choix de type de produit
TYPE_PRODUIT_CHOICES = [
    ('recolte', 'Récolte'),
    ('semence', 'Semence'),
    ('engrais', 'Engrais'),
    ('pesticide', 'Pesticide'),
    ('autre', 'Autre'),
]


# Méthode de suppression de produit
def delete_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    try:
        produit.delete()
        messages.success(request, "Produit supprimé avec succès.")
    except:
        messages.error(request, "Erreur lors de la suppression du produit.")
    return redirect('manage_produit')

# Formulaire d'ajout de commande
class AddCommandeForm(forms.Form):
    produit_id = forms.IntegerField(
        label="ID du Produit",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    quantite_commande = forms.FloatField(
        label="Quantité Commandée",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"})
    )
    date_commande = forms.DateField(
        label="Date de la Commande",
        widget=DateInput(attrs={"class": "form-control"})
    )

# Formulaire d'édition de commande
class EditCommandeForm(forms.Form):
    produit_id = forms.IntegerField(
        label="ID du Produit",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    quantite_commande = forms.FloatField(
        label="Quantité Commandée",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    date_commande = forms.DateField(
        label="Date de la Commande",
        widget=DateInput(attrs={"class": "form-control"})
    )

# Méthode de suppression de commande
def delete_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    try:
        commande.delete()
        messages.success(request, "Commande supprimée avec succès.")
    except:
        messages.error(request, "Erreur lors de la suppression de la commande.")
    return redirect('manage_commandes')

# Choix de rôles
ROLE_CHOICES = [
    ('client', 'Client'),
    ('agriculteur', 'Agriculteur'),
]

# Formulaire d'ajout d'utilisateur
class AddUtilisateurForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        label="Email",
        max_length=100,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    first_name = forms.CharField(
        label="Prénom",
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label="Nom de famille",
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    role = forms.ChoiceField(
        label="Rôle de l'utilisateur",
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    def save(self, commit=True):
        user = CustomUser(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            role=self.cleaned_data['role'],
        )
        user.set_password(self.cleaned_data['password'])  # hash le mot de passe
        if commit:
            user.save()
        return user
# Formulaire d'édition d'utilisateur
class EditUtilisateurForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    first_name = forms.CharField(
        label="Prénom",
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label="Nom de famille",
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    role = forms.ChoiceField(
        label="Rôle",
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )

# Méthode de suppression d'utilisateur
def delete_utilisateur(request, user_id):
    utilisateur = get_object_or_404(CustomUser, id=user_id)
    try:
        utilisateur.delete()
        messages.success(request, "Utilisateur supprimé avec succès.")
    except:
        messages.error(request, "Erreur lors de la suppression de l'utilisateur.")
    return redirect('manage_utilisateurs')

class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['produit', 'type_mouvement', 'quantite', 'commentaire']
        
User = get_user_model()
class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['client', 'statut']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On filtre pour ne voir que les clients (role='3')
        self.fields['client'].queryset = CustomUser.objects.filter(role='3')
        self.fields['client'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name} ({obj.email})"
# DetailCommandeForm est défini plus bas dans le fichier
# DetailCommandeFormSet est défini plus bas dans le fichier
# class LigneCommandeForm(forms.ModelForm):
#     class Meta:
#         model = LigneCommande
#         fields = ['produit', 'quantite']
#         widgets = {
#             'produit': forms.Select(attrs={'class': 'form-select'}),
#             'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
#         }

# LigneCommandeFormSet = inlineformset_factory(
#     Commande, LigneCommande, form=LigneCommandeForm,
#     extra=1, can_delete=True
# )
class LigneCommandeForm(forms.Form):
    produit = forms.ModelChoiceField(queryset=Produit.objects.all(), widget=forms.Select(attrs={'class':'form-select'}))
    quantite = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class':'form-control', 'min': 1}))

# Formset (tu peux régler extra)
LigneCommandeFormSet = formset_factory(LigneCommandeForm, extra=1, validate_min=True)
class ClientCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']  # adapte selon ton modèle

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # hash le mot de passe
        user.role = 'Client'  # force le rôle Client
        if commit:
            user.save()
        return user

User = get_user_model()

class ClientForm(forms.ModelForm):
    # Champs obligatoires
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choisissez un mot de passe sécurisé',
            'minlength': '8',
            'data-toggle': 'tooltip',
            'title': 'Le mot de passe doit contenir au moins 8 caractères, une majuscule et un chiffre'
        }),
        label="Mot de passe",
        help_text="Minimum 8 caractères, avec au moins une majuscule et un chiffre"
    )
    
    gender = forms.ChoiceField(
        choices=CustomUser.GENDER_CHOICES,
        label="Sexe",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Sélectionnez un genre'
        })
    )
    
    # Champs d'information personnelle
    first_name = forms.CharField(
        max_length=30,
        label="Prénom",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom du client'
        }),
        required=True
    )
    
    last_name = forms.CharField(
        max_length=30,
        label="Nom de famille",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom de famille du client'
        }),
        required=True
    )
    
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@exemple.com'
        }),
        required=True
    )
    
    # Champs de contact
    phone_number = forms.CharField(
        max_length=15,
        label="Téléphone portable",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: +221 77 123 45 67',
            'pattern': '^[+0-9\s-]+$'
        }),
        help_text="Format: +221 77 123 45 67 ou 77 123 45 67",
        required=True
    )
    
    phone_number_alt = forms.CharField(
        max_length=15,
        label="Téléphone secondaire (optionnel)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Téléphone secondaire (optionnel)'
        }),
        required=False
    )
    
    # Adresse
    address = forms.CharField(
        label="Adresse",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Adresse complète du client'
        }),
        required=True
    )
    
    city = forms.CharField(
        max_length=100,
        label="Ville",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ville de résidence'
        }),
        required=True
    )
    
    postal_code = forms.CharField(
        max_length=10,
        label="Code postal",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Code postal'
        }),
        required=False
    )
    
    country = forms.CharField(
        max_length=100,
        label="Pays",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'value': 'Sénégal',
            'readonly': 'readonly'
        }),
        initial='Sénégal',
        required=True
    )
    
    # Informations supplémentaires
    date_of_birth = forms.DateField(
        label="Date de naissance",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        required=False,
        help_text="Format: JJ/MM/AAAA"
    )
    
    notes = forms.CharField(
        label="Notes supplémentaires",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Informations complémentaires sur le client'
        }),
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur unique',
                'autocomplete': 'username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemple.com',
                'autocomplete': 'email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom',
                'autocomplete': 'given-name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de famille',
                'autocomplete': 'family-name'
            }),
        }
        help_texts = {
            'username': 'Requis. 150 caractères maximum. Lettres, chiffres et @/./+/-/_ uniquement.',
        }
        error_messages = {
            'username': {
                'unique': 'Ce nom d\'utilisateur est déjà utilisé.',
            },
            'email': {
                'unique': 'Cette adresse email est déjà utilisée.',
            },
        }
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une lettre majuscule.")
        return password
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Nettoyer le numéro de téléphone
        phone_number = ''.join(filter(str.isdigit, phone_number))
        if len(phone_number) < 9:
            raise forms.ValidationError("Le numéro de téléphone doit contenir au moins 9 chiffres.")
        return phone_number
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email
    
    # Ancienne méthode save remplacée par la nouvelle version ci-dessous

    def save(self, commit=True):
        user = super().save(commit=False)
        # Paramètres utilisateur
        user.is_active = True
        user.role = 'Client'
        user.telephone = self.cleaned_data.get('phone_number', '')
        
        # Gestion du genre
        gender = self.cleaned_data.get('gender')
        if gender in ['M', 'F']:
            user.gender = gender
            
        # Définir le type d'utilisateur
        try:
            user.user_type = CustomUser.CLIENT  # '3'
        except Exception:
            user.user_type = '3'
            
        # Définir le mot de passe
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
            
        if commit:
            user.save()
            # Créer le profil Client
            from .models import Client  # import local pour éviter import cycle
            Client.objects.create(
                admin=user,
                nom=f"{user.first_name} {user.last_name}",
                address=self.cleaned_data.get('address', ''),
                city=self.cleaned_data.get('city', ''),
                postal_code=self.cleaned_data.get('postal_code', ''),
                country=self.cleaned_data.get('country', 'Sénégal'),
                phone_number=self.cleaned_data.get('phone_number', ''),
                phone_number_alt=self.cleaned_data.get('phone_number_alt', ''),
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                notes=self.cleaned_data.get('notes', '')
            )
        return user
    
class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom_produit', 'type_produit', 'quantite', 'prix_unitaire', 'image', 'image_static']
        widgets = {
            'nom_produit': forms.TextInput(attrs={'class': 'form-control'}),
            'type_produit': forms.TextInput(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'image_static': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "ex: dist/img/sorgho.jpg"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        quantite = cleaned_data.get('quantite')
        prix_unitaire = cleaned_data.get('prix_unitaire')

        if quantite is not None and prix_unitaire is not None:
            cleaned_data['montant_total'] = quantite * prix_unitaire  # 👈 Calcul automatique

        return cleaned_data
class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['produit', 'quantite']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type_transaction', 'montant', 'description']
        widgets = {
            'type_transaction': forms.Select(attrs={'class': 'form-select'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
class AgriculteurForm(forms.ModelForm):
    GENDER_CHOICES = (
        ('M', 'Homme'),
        ('F', 'Femme'),
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'gender']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get("password")
        if pwd:
            user.set_password(pwd)  # hash du mot de passe
        if commit:
            user.save()
        return user
class DetailCommandeForm(forms.ModelForm):
    class Meta:
        model = DetailCommande
        fields = ['produit', 'quantite', 'prix_unitaire']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser l'affichage des produits dans le select
        self.fields['produit'].queryset = Produit.objects.all()
        self.fields['produit'].label_from_instance = lambda obj: f"{obj.nom_produit} ({obj.quantite} en stock)"

    def clean(self):
        cd = super().clean()
        produit = cd.get('produit')
        quantite = cd.get('quantite')
        if produit and quantite:
            if quantite > produit.quantite:
                raise forms.ValidationError(
                    f"Stock insuffisant ({produit.quantite} disponibles)."
                )
        return cd

DetailCommandeFormSet = inlineformset_factory(
    Commande, DetailCommande,
    form=DetailCommandeForm,
    fields=['produit', 'quantite', 'prix_unitaire'],
    extra=1,
    can_delete=True
)


class DepenseRevenuForm(forms.ModelForm):
    class Meta:
        model = DepenseRevenu
        fields = ['type', 'montant', 'date', 'description', 'quantite', 'prix_unitaire']
        widgets = {
            'date': DateInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class SemencePlantForm(forms.ModelForm):
    """
    Formulaire pour l'ajout et la modification de semences et plants
    """
    TYPE_CHOICES = [
        ('SEMENCE', 'Semence'),
        ('PLANT', 'Plant'),
    ]
    
    type_produit = forms.ChoiceField(
        choices=TYPE_CHOICES,
        label="Type de produit",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Produit
        fields = [
            'nom_produit', 'type_produit', 'prix_unitaire', 
            'quantite', 'image', 'image_static'
        ]
        widgets = {
            'nom_produit': forms.TextInput(attrs={'class': 'form-control'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'nom_produit': 'Nom du produit',
            'prix_unitaire': 'Prix unitaire (FCFA)',
            'quantite': 'Quantité en stock',
            'image': 'Image du produit',
            'image_static': 'Chemin de l\'image statique',
        }
    
    def clean_prix_unitaire(self):
        prix_unitaire = self.cleaned_data.get('prix_unitaire')
        if prix_unitaire <= 0:
            raise forms.ValidationError("Le prix unitaire doit être supérieur à zéro.")
        return prix_unitaire
    
    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        if quantite < 0:
            raise forms.ValidationError("La quantité ne peut pas être négative.")
        return quantite

# Formulaires pour la gestion des cultures
class CultureForm(forms.ModelForm):
    class Meta:
        model = Culture
        fields = [
            'nom', 'type_culture', 'description', 'duree_cycle',
            'besoins_eau', 'besoins_nutriments', 'periode_semis_optimale',
            'rendement_moyen', 'est_actif'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type_culture': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duree_cycle': forms.NumberInput(attrs={'class': 'form-control'}),
            'besoins_eau': forms.TextInput(attrs={'class': 'form-control'}),
            'besoins_nutriments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'periode_semis_optimale': forms.TextInput(attrs={'class': 'form-control'}),
            'rendement_moyen': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nom': 'Nom de la culture',
            'type_culture': 'Type de culture',
            'description': 'Description',
            'duree_cycle': 'Durée du cycle (jours)',
            'besoins_eau': 'Besoins en eau',
            'besoins_nutriments': 'Besoins en nutriments',
            'periode_semis_optimale': 'Période de semis optimale',
            'rendement_moyen': 'Rendement moyen (t/ha)',
            'est_actif': 'Culture active',
        }

# Formulaires pour la gestion des parcelles
class ParcelleForm(forms.ModelForm):
    class Meta:
        model = Parcelle
        fields = [
            'nom', 'code_unique', 'superficie', 'localisation', 
            'coordonnees_gps', 'type_sol', 'ph_sol', 'qualite_eau',
            'systeme_irrigation', 'statut', 'agriculteur', 'culture_actuelle',
            'notes', 'est_active'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'code_unique': forms.TextInput(attrs={'class': 'form-control'}),
            'superficie': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'localisation': forms.TextInput(attrs={'class': 'form-control'}),
            'coordonnees_gps': forms.TextInput(attrs={'class': 'form-control'}),
            'type_sol': forms.Select(attrs={'class': 'form-select'}),
            'ph_sol': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'qualite_eau': forms.TextInput(attrs={'class': 'form-control'}),
            'systeme_irrigation': forms.TextInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'agriculteur': forms.Select(attrs={'class': 'form-select'}),
            'culture_actuelle': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'est_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nom': 'Nom de la parcelle',
            'code_unique': 'Code unique',
            'superficie': 'Superficie (hectares)',
            'localisation': 'Localisation',
            'coordonnees_gps': 'Coordonnées GPS',
            'type_sol': 'Type de sol',
            'ph_sol': 'pH du sol',
            'qualite_eau': 'Qualité de l\'eau',
            'systeme_irrigation': 'Système d\'irrigation',
            'statut': 'Statut',
            'agriculteur': 'Agriculteur assigné',
            'culture_actuelle': 'Culture actuelle',
            'notes': 'Notes supplémentaires',
            'est_active': 'Parcelle active',
        }

class ParcelleAssignationForm(forms.ModelForm):
    class Meta:
        model = Parcelle
        fields = ['agriculteur', 'culture_actuelle']
        widgets = {
            'agriculteur': forms.Select(attrs={'class': 'form-select'}),
            'culture_actuelle': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'agriculteur': 'Agriculteur à assigner',
            'culture_actuelle': 'Culture à planter',
        }

# Formulaires pour les itinéraires techniques
class ItineraireTechniqueForm(forms.ModelForm):
    class Meta:
        model = ItineraireTechnique
        fields = [
            'parcelle', 'culture', 'etape', 'description', 
            'date_planifiee', 'date_realisee', 'statut',
            'observations', 'responsable'
        ]
        widgets = {
            'parcelle': forms.Select(attrs={'class': 'form-select'}),
            'culture': forms.Select(attrs={'class': 'form-select'}),
            'etape': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_planifiee': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_realisee': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'parcelle': 'Parcelle',
            'culture': 'Culture',
            'etape': 'Étape',
            'description': 'Description de l\'étape',
            'date_planifiee': 'Date planifiée',
            'date_realisee': 'Date réalisée',
            'statut': 'Statut',
            'observations': 'Observations',
            'responsable': 'Responsable',
        }

# Formulaires pour les activités agricoles
class ActiviteAgricoleForm(forms.ModelForm):
    class Meta:
        model = ActiviteAgricole
        fields = [
            'parcelle', 'culture', 'type_activite', 'titre', 'description',
            'date_planifiee', 'date_debut', 'date_fin', 'statut',
            'agriculteur', 'responsable', 'observations'
        ]
        widgets = {
            'parcelle': forms.Select(attrs={'class': 'form-select'}),
            'culture': forms.Select(attrs={'class': 'form-select'}),
            'type_activite': forms.Select(attrs={'class': 'form-select'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_planifiee': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'date_debut': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'date_fin': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'agriculteur': forms.Select(attrs={'class': 'form-select'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'parcelle': 'Parcelle',
            'culture': 'Culture',
            'type_activite': 'Type d\'activité',
            'titre': 'Titre de l\'activité',
            'description': 'Description',
            'date_planifiee': 'Date planifiée',
            'date_debut': 'Heure de début',
            'date_fin': 'Heure de fin',
            'statut': 'Statut',
            'agriculteur': 'Agriculteur',
            'responsable': 'Responsable',
            'observations': 'Observations',
        }

class ActiviteValidationForm(forms.Form):
    motif_refus = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Motif du refus (si refus)"
    )
    action = forms.ChoiceField(
        choices=[
            ('valider', 'Valider l\'activité'),
            ('refuser', 'Refuser l\'activité')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Action"
    )


# ==================== FORMULAIRES POUR TECHNICIEN AGRONOME ====================

class FicheConseilForm(forms.ModelForm):
    """Formulaire pour créer et modifier les fiches-conseils"""
    
    class Meta:
        model = FicheConseil
        fields = [
            'titre', 'description', 'contenu', 'recommandations', 
            'periode_optimale', 'difficulte', 'culture', 'type_culture', 
            'categorie', 'image', 'publie'
        ]
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la fiche-conseil'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description résumée de la fiche...'
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Contenu détaillé avec instructions complètes...'
            }),
            'recommandations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Recommandations principales à retenir...'
            }),
            'periode_optimale': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Mars-Avril, Saison des pluies...'
            }),
            'difficulte': forms.Select(attrs={'class': 'form-control'}),
            'culture': forms.Select(attrs={'class': 'form-control'}),
            'type_culture': forms.Select(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'publie': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les cultures disponibles
        self.fields['culture'].queryset = Culture.objects.all()
        self.fields['culture'].empty_label = "Toutes les cultures"
        
        # Labels personnalisés
        self.fields['titre'].label = "Titre de la fiche-conseil"
        self.fields['description'].label = "Description résumée"
        self.fields['contenu'].label = "Contenu détaillé"
        self.fields['recommandations'].label = "Recommandations principales"
        self.fields['periode_optimale'].label = "Période optimale"
        self.fields['difficulte'].label = "Niveau de difficulté"
        self.fields['culture'].label = "Culture spécifique (optionnel)"
        self.fields['type_culture'].label = "Type de culture"
        self.fields['categorie'].label = "Catégorie"
        self.fields['image'].label = "Image illustrative"
        self.fields['publie'].label = "Publier cette fiche-conseil"


class RecommandationForm(forms.Form):
    """Formulaire simple pour ajouter une recommandation lors de la validation"""
    
    recommandation = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Donnez vos recommandations spécifiques à l\'agriculteur...'
        }),
        label="Recommandation du technicien",
        required=True,
        help_text="Soyez précis et constructif dans vos recommandations."
    )


class PhotoValidationForm(forms.ModelForm):
    """Formulaire pour valider une photo avec commentaire"""
    
    class Meta:
        model = PhotoCulture
        fields = ['commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Commentaire sur la photo...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['commentaire'].label = "Commentaire du technicien"
        self.fields['commentaire'].help_text = "Ajoutez vos observations ou recommandations."
