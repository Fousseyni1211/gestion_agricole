from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User

from django.conf import settings
from django.contrib.auth import get_user_model
# Modèle pour gérer les années de session (pouvant être utile si vous voulez ajouter des périodes agricoles)
class SeasonYearModel(models.Model):
    id = models.AutoField(primary_key=True)
    season_start_date = models.DateField()
    season_end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.season_start_date} to {self.season_end_date}"

# Overriding the Default Django Auth User and adding one more field (user_type)
class CustomUser(AbstractUser):
    ADMIN = '1'
    CLIENT = '3'
    AGRICULTEUR = '4'
    
    USER_TYPE_CHOICES = (
        (ADMIN, "Admin"),
        (CLIENT, "Client"),
        (AGRICULTEUR, "Agriculteur"),
    )
    role = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    GENDER_CHOICES = (
        ('M', 'Homme'),
        ('F', 'Femme'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M', verbose_name='Genre')
    telephone = models.CharField(max_length=20, blank=True, null=True)
    # Ces champs doivent exister si tu veux les utiliser dans le formulaire :
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    # Liste des choix possibles pour le type d'utilisateur
    user_type_data = ((ADMIN, "ADMIN"), (AGRICULTEUR, "AGRICULTEUR"), (CLIENT, "CLIENT"))
    
    # Champ pour définir le type d'utilisateur
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10)
    
    EMAIL_TO_USER_TYPE_MAP = {
        'client': CLIENT,
        'agriculteur': AGRICULTEUR,
        'admin': ADMIN
    }

    # Modèle pour le Chef de Département (HOD), qui est une relation 1:1 avec CustomUser
class Admin(models.Model):
    id = models.AutoField(primary_key=True)  # ID auto-généré
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # Relation 1:1 avec CustomUser
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création automatique
    updated_at = models.DateTimeField(auto_now=True)  # Date de mise à jour automatique
    objects = models.Manager()  # Gestionnaire par défaut


# Modèle pour les clients
class Client(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100, verbose_name="Nom complet")
    admin = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_profile')
    
    # Coordonnées
    address = models.TextField(verbose_name="Adresse")
    city = models.CharField(max_length=100, verbose_name="Ville", blank=True, null=True)
    postal_code = models.CharField(max_length=10, verbose_name="Code postal", blank=True, null=True)
    country = models.CharField(max_length=100, default='Sénégal', verbose_name="Pays")
    
    # Coordonnées téléphoniques
    phone_number = models.CharField(max_length=20, verbose_name="Téléphone principal")
    phone_number_alt = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone secondaire")
    
    # Informations supplémentaires
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Date de naissance")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes supplémentaires")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nom} ({self.phone_number})"
    
    def get_full_name(self):
        return f"{self.nom} ({self.admin.first_name} {self.admin.last_name})"


# Modèle pour les agriculteurs
class Agriculteur(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, default=1)  # Relation 1:1 avec CustomUser
    farm_name = models.CharField(max_length=255)
    address = models.TextField()
    farm_area = models.FloatField(help_text="Area in hectares")
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return self.farm_name
    
class Category(models.Model):
    # admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE) # Relation 1:1 avec CustomUser
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

# Modèle pour les produits agricoles
class Produit(models.Model):
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_static = models.CharField(max_length=255, blank=True, null=True, help_text="Chemin relatif dans static, ex: 'dist/img/sorgho.jpg'")
    nom_produit = models.CharField(max_length=100, unique=True)  # Unique !
    type_produit = models.CharField(max_length=100)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    seuil_alerte = models.PositiveIntegerField(default=10)
    fournisseur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='produits', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom_produit} ({self.type_produit})"

    def save(self, *args, **kwargs):
        self.montant_total = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)

    def update_stock(self, quantity):
        if self.quantite + quantity < 0:
            raise ValueError("Stock insuffisant pour le retrait.")
        self.quantite += quantity
        self.save()

    def est_en_alerte(self):
        return self.quantite < self.seuil_alerte

# Modèle pour gérer les commandes des clients
# ✅ Modèle Commande
class Commande(models.Model):
    STATUTS = [
        ('en_attente', 'En attente de validation'),
        ('en_attente_paiement', 'En attente de paiement'),
        ('payee_en_attente', 'Payée - En attente de validation gérant'),
        ('paiement_echoue', 'Paiement échoué'),
        ('validee', 'Validée et traitée'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'Client'}
    )
    date_commande = models.DateTimeField(auto_now_add=True, editable=False)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gérant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commandes_gererees',
        limit_choices_to={'user_type': '1'}
    )

    def get_total(self):
        return sum(detail.prix * detail.quantite for detail in self.details.all())
    
    def verifier_disponibilite_stock(self):
        """Vérifie si tous les produits de la commande sont disponibles en stock"""
        for detail in self.details.all():
            stock = Stock.get_or_create_stock(self.gérant, detail.produit)
            if not stock.peut_satisfaire(detail.quantite):
                return False, f"Stock insuffisant pour {detail.produit.nom_produit}. Disponible: {stock.quantite}, Demandé: {detail.quantite}"
        return True, "Stock disponible"
    
    def valider_et_reduire_stock(self):
        """Valide la commande et réduit automatiquement le stock"""
        if self.statut != 'en_attente':
            raise ValueError("Seules les commandes en attente peuvent être validées")
        
        # Vérifier la disponibilité du stock
        disponible, message = self.verifier_disponibilite_stock()
        if not disponible:
            raise ValueError(message)
        
        # Réduire le stock pour chaque produit
        for detail in self.details.all():
            stock = Stock.get_or_create_stock(self.gérant, detail.produit)
            stock.reduire_stock(
                detail.quantite, 
                f"Vente - Commande #{self.id} - Client: {self.client.username}"
            )
        
        # Mettre à jour le statut de la commande
        self.statut = 'validee'
        self.save()
        
        return True, "Commande validée et stock mis à jour"
    
    def annuler_et_restituer_stock(self):
        """Annule la commande et restitue le stock"""
        if self.statut in ['livree', 'annulee']:
            raise ValueError("Impossible d'annuler une commande déjà livrée ou annulée")
        
        # Restituer le stock pour chaque produit
        for detail in self.details.all():
            stock = Stock.get_or_create_stock(self.gérant, detail.produit)
            stock.augmenter_stock(
                detail.quantite,
                f"Annulation - Commande #{self.id} - Client: {self.client.username}"
            )
        
        # Mettre à jour le statut de la commande
        self.statut = 'annulee'
        self.save()
        
        return True, "Commande annulée et stock restitué"
    
    def get_stock_status(self):
        """Retourne le statut de stock pour chaque produit de la commande"""
        status = {}
        for detail in self.details.all():
            stock = Stock.get_or_create_stock(self.gérant, detail.produit)
            status[detail.produit.nom_produit] = {
                'disponible': stock.quantite,
                'demande': detail.quantite,
                'suffisant': stock.peut_satisfaire(detail.quantite),
                'en_alerte': stock.est_en_alerte(),
                'en_rupture': stock.est_en_rupture()
            }
        return status
    
    def __str__(self):
        return f"Commande #{self.id} - {self.client.username}"

class DetailCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='details')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def sous_total(self):
        return self.quantite * self.prix_unitaire
    def save(self, *args, **kwargs):
        if self.quantite < 0:
            raise ValueError("Le stock ne peut pas être négatif.")
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.produit.nom_produit} x {self.quantite}"


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    sous_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.produit.nom_produit} x{self.quantite}"
# Modèle pour gérer les paiements
class Paiement(models.Model):
    id = models.AutoField(primary_key=True)
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="paiements", default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('orange_money', 'Orange Money'),
            ('wave', 'Wave'),
            ('a_la_livraison', 'Paiement à la livraison'),
        ],
        default='a_la_livraison'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'En attente'), ('Validated', 'Validé'), ('Rejected', 'Rejeté'), ('Refunded', 'Remboursé')],
        default='Pending'
    )

    payment_date = models.DateTimeField(default=timezone.now)  # ✅ PAS de parenthèses
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order {self.commande.id} - {self.amount} FCFA"

    def save(self, *args, **kwargs):
        if self.payment_status == 'Validated':
            self.commande.statut = 'payee'
            self.commande.save()
        super().save(*args, **kwargs)
    
class Stock(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=0)
    derniere_mise_a_jour = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['utilisateur', 'produit']
        ordering = ['produit__nom_produit']
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.produit.nom_produit}: {self.quantite}"
    
    def est_en_rupture(self):
        """Vérifie si le stock est en rupture (quantité <= 0)"""
        return self.quantite <= 0
    
    def est_en_alerte(self):
        """Vérifie si le stock est en alerte (quantité < seuil_alerte)"""
        return self.quantite < self.produit.seuil_alerte
    
    def quantite_disponible(self):
        """Retourne la quantité disponible pour la vente"""
        return max(0, self.quantite)
    
    def peut_satisfaire(self, quantite_demandee):
        """Vérifie si le stock peut satisfaire une demande"""
        return self.quantite >= quantite_demandee
    
    def reduire_stock(self, quantite, commentaire=""):
        """Réduit le stock et crée un mouvement de sortie"""
        if quantite <= 0:
            raise ValueError("La quantité à réduire doit être positive")
        
        if not self.peut_satisfaire(quantite):
            raise ValueError(f"Stock insuffisant. Disponible: {self.quantite}, Demandé: {quantite}")
        
        # Créer le mouvement de sortie
        MouvementStock.objects.create(
            produit=self.produit,
            type_mouvement=MouvementStock.SORTIE,
            quantite=quantite,
            commentaire=commentaire or f"Sortie automatique - Stock restant: {self.quantite - quantite}"
        )
        
        # Réduire la quantité
        self.quantite -= quantite
        self.save()
    
    def augmenter_stock(self, quantite, commentaire=""):
        """Augmente le stock et crée un mouvement d'entrée"""
        if quantite <= 0:
            raise ValueError("La quantité à ajouter doit être positive")
        
        # Créer le mouvement d'entrée
        MouvementStock.objects.create(
            produit=self.produit,
            type_mouvement=MouvementStock.ENTREE,
            quantite=quantite,
            commentaire=commentaire or f"Entrée automatique - Nouveau stock: {self.quantite + quantite}"
        )
        
        # Augmenter la quantité
        self.quantite += quantite
        self.save()
    
    @classmethod
    def get_or_create_stock(cls, utilisateur, produit):
        """Récupère ou crée un enregistrement de stock pour un utilisateur et produit"""
        stock, created = cls.objects.get_or_create(
            utilisateur=utilisateur,
            produit=produit,
            defaults={'quantite': 0}
        )
        return stock

class MouvementStock(models.Model):
    ENTREE = 'ENTREE'
    SORTIE = 'SORTIE'
    TYPE_MOUVEMENT = [
        (ENTREE, 'Entrée'),
        (SORTIE, 'Sortie'),
    ]
    
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    type_mouvement = models.CharField(max_length=6, choices=TYPE_MOUVEMENT)
    quantite = models.PositiveIntegerField()
    date = models.DateTimeField(default=timezone.now)
    commentaire = models.TextField(blank=True, null=True)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reference = models.CharField(max_length=100, blank=True, null=True, help_text="Référence de la commande ou de l'opération")
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
    
    def __str__(self):
        return f"{self.get_type_mouvement_display()} - {self.produit.nom_produit} ({self.quantite}) - {self.date.strftime('%d/%m/%Y')}"
    
    @classmethod
    def creer_mouvement_vente(cls, produit, quantite, commande, utilisateur=None):
        """Crée un mouvement de sortie lié à une vente"""
        return cls.objects.create(
            produit=produit,
            type_mouvement=cls.SORTIE,
            quantite=quantite,
            commentaire=f"Vente - Commande #{commande.id}",
            utilisateur=utilisateur,
            reference=f"CMD-{commande.id}"
        )
    
    @classmethod
    def creer_mouvement_retour(cls, produit, quantite, commande, utilisateur=None):
        """Crée un mouvement d'entrée lié à un retour de commande"""
        return cls.objects.create(
            produit=produit,
            type_mouvement=cls.ENTREE,
            quantite=quantite,
            commentaire=f"Retour - Commande #{commande.id}",
            utilisateur=utilisateur,
            reference=f"RET-CMD-{commande.id}"
        )

# Suppression de la duplication du modèle Client
# Modèle pour les notifications
class Notification(models.Model):
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Succès'),
        ('warning', 'Avertissement'),
        ('danger', 'Urgent'),
        ('primary', 'Primaire'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    url = models.URLField(blank=True, null=True, help_text="URL de redirection lors du clic sur la notification")
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Classe d'icône (ex: 'fas fa-bell')")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.get_type_display()} - {self.message[:50]}..."
        
    def mark_as_read(self):
        """Marque la notification comme lue"""
        self.is_read = True
        self.save(update_fields=['is_read', 'updated_at'])
        
    def mark_as_unread(self):
        """Marque la notification comme non lue"""
        if self.is_read:
            self.is_read = False
            self.updated_at = timezone.now()
            self.save(update_fields=['is_read', 'updated_at'])
            return True
        return False
        
    def get_time_ago(self):
        """Retourne une chaîne indiquant le temps écoulé depuis la création"""
        now = timezone.now()
        diff = now - self.created_at
        
        if diff.days > 30:
            return f"il y a {diff.days // 30} mois"
        if diff.days > 0:
            return f"il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
        if diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"il y a {hours} heure{'s' if hours > 1 else ''}"
        if diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"il y a {minutes} minute{'s' if minutes > 1 else ''}"
        return "à l'instant"
        
    def get_absolute_url(self):
        """Retourne l'URL de la notification ou l'URL par défaut"""
        return self.url or reverse('notification_list')
        
    def get_icon_class(self):
        """Retourne la classe CSS de l'icône de la notification"""
        if self.icon:
            return self.icon
        return self.get_default_icon(self.type)
        
    def mark_as_read(self):
        """Marque la notification comme lue"""
        if not self.is_read:
            self.is_read = True
            self.updated_at = timezone.now()
            self.save(update_fields=['is_read', 'updated_at'])
            return True
        return False
        
    def mark_as_unread(self):
        """Marque la notification comme non lue"""
        if self.is_read:
            self.is_read = False
            self.updated_at = timezone.now()
            self.save(update_fields=['is_read', 'updated_at'])
            return True
        return False
        
    @classmethod
    def get_unread_count(cls, user):
        """Retourne le nombre de notifications non lues pour un utilisateur"""
        return cls.objects.filter(user=user, is_read=False).count()
        
    @classmethod
    def get_recent_notifications(cls, user, limit=5):
        """Retourne les notifications récentes pour un utilisateur"""
        return cls.objects.filter(user=user).order_by('-created_at')[:limit]
        
    @classmethod
    def create_notification(cls, user, message, notification_type='info', url=None, icon=None):
        """Crée une nouvelle notification pour un utilisateur"""
        return cls.objects.create(
            user=user,
            message=message,
            type=notification_type,
            url=url,
            icon=icon or cls.get_default_icon(notification_type)
        )
        
    @classmethod
    def mark_all_as_read(cls, user):
        """Marque toutes les notifications comme lues pour un utilisateur"""
        return cls.objects.filter(user=user, is_read=False).update(
            is_read=True,
            updated_at=timezone.now()
        )
        
    @staticmethod
    def get_default_icon(notification_type):
        """Retourne une icône par défaut selon le type de notification"""
        icons = {
            'info': 'fas fa-info-circle',
            'success': 'fas fa-check-circle',
            'warning': 'fas fa-exclamation-triangle',
            'danger': 'fas fa-exclamation-circle',
            'primary': 'fas fa-bell',
        }
        return icons.get(notification_type, 'fas fa-bell')

# Création de signaux Django pour l'automatisation des actions
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Cette fonction est exécutée après la création d'un utilisateur.
    Elle crée automatiquement un profil d'utilisateur spécifique (ADMIN, Fournisseur, Agriculteur, ou Client)
    en fonction du type d'utilisateur (user_type).
    """
    if created:
        # Si l'utilisateur est un HOD (Chef de Département), créer un profil Admin
        if instance.user_type == 1:
            Admin.objects.create(admin=instance)
        # Si l'utilisateur est un étudiant (Student), créer un profil Students
        if instance.user_type == 3:
            Client.objects.create(admin=instance)
        # Si l'utilisateur est un agriculteur, créer un profil agriculteur
        if instance.user_type == 4:
            Agriculteur.objects.create(
                admin=instance,
                farm_name="Ferme par défaut",
                address="",  # Valeur vide par défaut pour l'adresse
                farm_area=0.0,  # Valeur par défaut pour la superficie
                phone_number=""  # Valeur vide pour le numéro de téléphone
            )

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    Cette fonction est exécutée après la sauvegarde d'un utilisateur. 
    Elle assure que les profils (Admin, Fournisseur, Agriculteur, Client) sont bien sauvegardés 
    en fonction du type d'utilisateur (user_type).
    """
    if instance.user_type == 1:
        instance.admin.save()  # Sauvegarde du profil AdminHOD
    if instance.user_type == 3:
        instance.client.save()  # Sauvegarde du profil Client
    if instance.user_type == 4:
        instance.agriculteur.save()  # Sauvegarde du profil Agriculteur

class Culture(models.Model):
    TYPE_CULTURE_CHOICES = [
        ('mais', 'Maïs'),
        ('riz', 'Riz'),
        ('oignon', 'Oignon'),
        ('mil', 'Mil'),
        ('arachide', 'Arachide'),
        ('sorgho', 'Sorgho'),
        ('tomate', 'Tomate'),
        ('poivron', 'Poivron'),
        ('aubergine', 'Aubergine'),
        ('carotte', 'Carotte'),
        ('chou', 'Chou'),
        ('autre', 'Autre')
    ]
    
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la culture")
    type_culture = models.CharField(max_length=20, choices=TYPE_CULTURE_CHOICES, verbose_name="Type de culture")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    duree_cycle = models.PositiveIntegerField(default=90, help_text="Durée du cycle en jours", verbose_name="Durée du cycle (jours)")
    besoins_eau = models.CharField(max_length=100, blank=True, null=True, verbose_name="Besoins en eau")
    besoins_nutriments = models.TextField(blank=True, null=True, verbose_name="Besoins en nutriments")
    periode_semis_optimale = models.CharField(max_length=100, blank=True, null=True, verbose_name="Période de semis optimale")
    rendement_moyen = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Rendement moyen en tonnes/hectare", verbose_name="Rendement moyen (t/ha)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    est_actif = models.BooleanField(default=True, verbose_name="Culture active")

    class Meta:
        verbose_name = "Culture"
        verbose_name_plural = "Cultures"
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.get_type_culture_display()})"

class Parcelle(models.Model):
    TYPE_SOL_CHOICES = [
        ('argileux', 'Argileux'),
        ('limoneux', 'Limoneux'),
        ('sableux', 'Sableux'),
        ('calcaire', 'Calcaire'),
        ('humifere', 'Humifère'),
        ('autre', 'Autre')
    ]
    
    STATUT_PARCELLE = [
        ('disponible', 'Disponible'),
        ('occupee', 'Occupée'),
        ('en_preparation', 'En préparation'),
        ('en_repos', 'En repos'),
        ('maintenance', 'En maintenance')
    ]
    
    nom = models.CharField(max_length=100, verbose_name="Nom de la parcelle")
    code_unique = models.CharField(max_length=50, unique=True, verbose_name="Code unique de la parcelle")
    superficie = models.DecimalField(max_digits=8, decimal_places=2, help_text="Superficie en hectares", verbose_name="Superficie (ha)")
    localisation = models.CharField(max_length=255, verbose_name="Localisation")
    coordonnees_gps = models.CharField(max_length=100, blank=True, null=True, verbose_name="Coordonnées GPS")
    type_sol = models.CharField(max_length=20, choices=TYPE_SOL_CHOICES, verbose_name="Type de sol")
    ph_sol = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name="pH du sol")
    qualite_eau = models.CharField(max_length=100, blank=True, null=True, verbose_name="Qualité de l'eau")
    systeme_irrigation = models.CharField(max_length=100, blank=True, null=True, verbose_name="Système d'irrigation")
    statut = models.CharField(max_length=20, choices=STATUT_PARCELLE, default='disponible', verbose_name="Statut")
    agriculteur = models.ForeignKey(Agriculteur, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Agriculteur assigné")
    culture_actuelle = models.ForeignKey(Culture, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Culture actuelle")
    date_assignation = models.DateField(blank=True, null=True, verbose_name="Date d'assignation")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes supplémentaires")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    est_active = models.BooleanField(default=True, verbose_name="Parcelle active")

    class Meta:
        verbose_name = "Parcelle"
        verbose_name_plural = "Parcelles"
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.code_unique}) - {self.superficie}ha"
    
    def assigner_agriculteur(self, agriculteur, culture=None):
        """Assigne un agriculteur et une culture à la parcelle"""
        self.agriculteur = agriculteur
        self.culture_actuelle = culture
        self.statut = 'occupee'
        self.date_assignation = timezone.now().date()
        self.save()
    
    def liberer_parcelle(self):
        """Libère la parcelle de l'agriculteur et de la culture"""
        self.agriculteur = None
        self.culture_actuelle = None
        self.statut = 'disponible'
        self.date_assignation = None
        self.save()

class ItineraireTechnique(models.Model):
    ETAPE_CHOICES = [
        ('preparation_sol', 'Préparation du sol'),
        ('semis', 'Semis'),
        ('fertilisation', 'Fertilisation'),
        ('irrigation', 'Irrigation'),
        ('desherbage', 'Désherbage'),
        ('traitement_phytosanitaire', 'Traitement phytosanitaire'),
        ('recolte', 'Récolte'),
        ('post_recolte', 'Post-récolte')
    ]
    
    STATUT_ETAPE = [
        ('planifie', 'Planifié'),
        ('en_cours', 'En cours'),
        ('realise', 'Réalisé'),
        ('retard', 'Retard'),
        ('annule', 'Annulé')
    ]
    
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, related_name='itineraires')
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE)
    etape = models.CharField(max_length=30, choices=ETAPE_CHOICES)
    description = models.TextField(verbose_name="Description de l'étape")
    date_planifiee = models.DateField(verbose_name="Date planifiée")
    date_realisee = models.DateField(blank=True, null=True, verbose_name="Date réalisée")
    statut = models.CharField(max_length=20, choices=STATUT_ETAPE, default='planifie')
    observations = models.TextField(blank=True, null=True, verbose_name="Observations")
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Responsable")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Itinéraire technique"
        verbose_name_plural = "Itinéraires techniques"
        ordering = ['date_planifiee']

    def __str__(self):
        return f"{self.get_etape_display()} - {self.parcelle.nom} ({self.culture.nom})"

class ActiviteAgricole(models.Model):
    TYPE_ACTIVITE = [
        ('semis', 'Semis'),
        ('traitement', 'Traitement'),
        ('irrigation', 'Irrigation'),
        ('fertilisation', 'Fertilisation'),
        ('recolte', 'Récolte'),
        ('surveillance', 'Surveillance'),
        ('maintenance', 'Maintenance'),
        ('autre', 'Autre')
    ]
    
    STATUT_ACTIVITE = [
        ('planifie', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
        ('en_attente_validation', 'En attente de validation')
    ]
    
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, related_name='activites')
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE)
    type_activite = models.CharField(max_length=20, choices=TYPE_ACTIVITE)
    titre = models.CharField(max_length=200, verbose_name="Titre de l'activité")
    description = models.TextField(verbose_name="Description")
    date_planifiee = models.DateTimeField(verbose_name="Date planifiée")
    date_debut = models.DateTimeField(blank=True, null=True, verbose_name="Heure de début")
    date_fin = models.DateTimeField(blank=True, null=True, verbose_name="Heure de fin")
    statut = models.CharField(max_length=25, choices=STATUT_ACTIVITE, default='planifie')
    agriculteur = models.ForeignKey(Agriculteur, on_delete=models.CASCADE, verbose_name="Agriculteur")
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Responsable")
    observations = models.TextField(blank=True, null=True, verbose_name="Observations")
    validee_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='activites_validees', verbose_name="Validée par")
    date_validation = models.DateTimeField(blank=True, null=True, verbose_name="Date de validation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Activité agricole"
        verbose_name_plural = "Activités agricoles"
        ordering = ['-date_planifiee']

    def __str__(self):
        return f"{self.get_type_activite_display()} - {self.parcelle.nom} ({self.get_statut_display()})"
    
    def valider_activite(self, validee_par):
        """Valide l'activité"""
        self.statut = 'terminee'
        self.validee_par = validee_par
        self.date_validation = timezone.now()
        self.save()
    
    def refuser_activite(self, validee_par, motif):
        """Refuse l'activité"""
        self.statut = 'annulee'
        self.validee_par = validee_par
        self.date_validation = timezone.now()
        self.observations = f"REFUSÉ: {motif}\n{self.observations or ''}"
        self.save()
class Alerte(models.Model):
    message = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='alertes'
    )

    def __str__(self):
        return self.message
class Meteo(models.Model):
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE)
    temperature = models.FloatField()
    condition = models.CharField(max_length=100)
    humidite = models.FloatField()
    vent = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Météo - {self.culture.nom} ({self.date.date()})"
User = get_user_model()

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('revenu', 'Revenu'),
        ('depense', 'Dépense'),
    ]

    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    type_transaction = models.CharField(max_length=10, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_transaction} - {self.montant}€ le {self.date}"


class DepenseRevenu(models.Model):
    TYPE_CHOICES = [
        ('DEPENSE', 'Dépense'),
        ('REVENU', 'Revenu'),
    ]

    agriculteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mouvements_financiers')
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    date = models.DateField()
    description = models.CharField(max_length=255)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    quantite = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Pour ventes : quantité vendue
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)  # Prix par unité (pour ventes)

    def __str__(self):
        return f"{self.get_type_display()} - {self.description} ({self.date})"
    
class MouvementFinance(models.Model):
    TYPE_CHOIX = [
        ('DEPENSE', 'Dépense'),
        ('REVENU', 'Revenu'),
    ]

    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOIX)

    def __str__(self):
        return f"{self.date} - {self.description} ({self.type})"
class Materiel(models.Model):
    CATEGORIES = [
        ('tracteur', 'Tracteur'),
        ('moissonneuse', 'Moissonneuse-batteuse'),
        ('pulverisateur', 'Pulvérisateur'),
        ('semoir', 'Semoir'),
        ('charrue', 'Charrue'),
        ('herse', 'Herse'),
        ('irrigation', 'Matériel d\'irrigation'),
        ('recolte', 'Matériel de récolte'),
        ('transport', 'Matériel de transport'),
        ('autre', 'Autre'),
    ]
    
    STATUTS = [
        ('disponible', 'Disponible'),
        ('indisponible', 'Indisponible'),
        ('maintenance', 'En maintenance'),
        ('reserve', 'Réservé'),
    ]
    
    nom = models.CharField(max_length=100, verbose_name="Nom du matériel")
    categorie = models.CharField(max_length=50, choices=CATEGORIES, verbose_name="Catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    photo = models.ImageField(upload_to='materiels/', blank=True, null=True, verbose_name="Photo")
    prix_location_jour = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de location par jour (FCFA)")
    statut = models.CharField(max_length=20, choices=STATUTS, default='disponible', verbose_name="Statut")
    disponible = models.BooleanField(default=True, verbose_name="Disponible à la location")
    
    # Informations supplémentaires
    marque = models.CharField(max_length=100, blank=True, null=True, verbose_name="Marque")
    modele = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modèle")
    annee_fabrication = models.PositiveIntegerField(blank=True, null=True, verbose_name="Année de fabrication")
    numero_serie = models.CharField(max_length=100, blank=True, null=True, verbose_name="Numéro de série")
    
    # Gestion de la disponibilité
    quantite_disponible = models.PositiveIntegerField(default=1, verbose_name="Quantité disponible")
    quantite_totale = models.PositiveIntegerField(default=1, verbose_name="Quantité totale")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Matériel agricole"
        verbose_name_plural = "Matériels agricoles"
        ordering = ['categorie', 'nom']
    
    def __str__(self):
        return f"{self.nom} ({self.get_categorie_display()})"
    
    def is_available_for_dates(self, date_debut, date_fin):
        """Vérifie si le matériel est disponible pour une période donnée"""
        if self.statut != 'disponible' or not self.disponible:
            return False
            
        # Vérifier les réservations existantes
        reservations_conflictuelles = self.reservations.filter(
            validee=True,
            date_debut__lte=date_fin,
            date_fin__gte=date_debut
        )
        
        # Calculer le nombre total d'unités réservées pour cette période
        total_reserve = 0
        for reservation in reservations_conflictuelles:
            total_reserve += 1  # On suppose 1 unité par réservation, à adapter si besoin
        
        return total_reserve < self.quantite_disponible
    
    def get_reservations_en_cours(self):
        """Retourne les réservations en cours ou futures validées"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.reservations.filter(
            validee=True,
            date_fin__gte=today
        ).order_by('date_debut')
    
    def get_next_availability(self):
        """Retourne la prochaine date de disponibilité"""
        reservations = self.get_reservations_en_cours()
        if not reservations:
            return None
        
        last_reservation = reservations.last()
        return last_reservation.date_fin + timezone.timedelta(days=1)


class ReservationMateriel(models.Model):
    STATUTS = [
        ('en_attente', 'En attente de validation'),
        ('validee', 'Validée'),
        ('en_cours', 'En cours de location'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]
    
    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE, related_name='reservations')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    date_reservation = models.DateTimeField(auto_now_add=True, verbose_name="Date de réservation")
    
    # Gestion du statut et de la validation
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente', verbose_name="Statut")
    validee = models.BooleanField(default=False, verbose_name="Validée")
    date_validation = models.DateTimeField(blank=True, null=True, verbose_name="Date de validation")
    
    # Informations de pricing
    prix_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Prix total")
    prix_jour_applique = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Prix par jour appliqué")
    
    # Gestion de la location
    date_debut_reelle = models.DateField(blank=True, null=True, verbose_name="Date de début réelle")
    date_fin_reelle = models.DateField(blank=True, null=True, verbose_name="Date de fin réelle")
    
    # Informations supplémentaires
    commentaire = models.TextField(blank=True, null=True, verbose_name="Commentaire")
    commentaire_annulation = models.TextField(blank=True, null=True, verbose_name="Motif d'annulation")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Réservation de matériel"
        verbose_name_plural = "Réservations de matériel"
        ordering = ['-date_reservation']
        
    def __str__(self):
        return f"Réservation de {self.materiel.nom} par {self.client.username} du {self.date_debut} au {self.date_fin}"
    
    def save(self, *args, **kwargs):
        # Calcul du prix total automatiquement
        if self.materiel and not self.prix_total:
            if not self.prix_jour_applique:
                self.prix_jour_applique = self.materiel.prix_location_jour
            
            if self.date_debut and self.date_fin:
                nb_jours = (self.date_fin - self.date_debut).days + 1
                self.prix_total = self.prix_jour_applique * nb_jours
        
        # Mise à jour de la date de validation
        if self.validee and not self.date_validation:
            from django.utils import timezone
            self.date_validation = timezone.now()
            self.statut = 'validee'
        elif not self.validee and self.date_validation:
            self.date_validation = None
            self.statut = 'en_attente'
        
        super().save(*args, **kwargs)
    
    def get_nombre_jours(self):
        """Retourne le nombre de jours de location"""
        if self.date_debut and self.date_fin:
            return (self.date_fin - self.date_debut).days + 1
        return 0
    
    def is_active(self):
        """Vérifie si la réservation est actuellement active"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.validee and self.date_debut <= today <= self.date_fin
    
    def can_be_cancelled(self):
        """Vérifie si la réservation peut être annulée"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.statut in ['en_attente', 'validee'] and self.date_debut > today
        
# Suppression de la duplication des modèles Materiel et ReservationMateriel

# ================== alerts/models.py ==================
class Alerte(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    lue = models.BooleanField(default=False)

# ================== feedback/models.py ==================
class Testimonial(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    texte = models.TextField()
    date = models.DateField(auto_now_add=True)
    approuve = models.BooleanField(default=False)

# Modèle pour les services offerts par l'application
class Service(models.Model):
    TYPES_SERVICE = [
        ('conseil', 'Conseil Agricole'),
        ('location', 'Location de Matériel'),
        ('produit', 'Produits Bio'),
        ('formation', 'Formation Agricole'),
        ('analyse', 'Analyse de Sol'),
        ('autre', 'Autre Service')
    ]
    
    nom = models.CharField(max_length=100)
    type_service = models.CharField(max_length=20, choices=TYPES_SERVICE)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duree = models.CharField(max_length=50, null=True, blank=True, help_text="Durée approximative du service (ex: '2 heures', '3 jours')")
    disponible = models.BooleanField(default=True)
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nom} ({self.get_type_service_display()})"

# Modèle pour les demandes de service
class DemandeService(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée')
    ]
    
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='demandes_service')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='demandes')
    date_demande = models.DateTimeField(auto_now_add=True)
    date_souhaitee = models.DateField(null=True, blank=True)
    message = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    commentaire_admin = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Demande de {self.service.nom} par {self.client.username} ({self.get_statut_display()})"
    
    class Meta:
        ordering = ['-date_demande']

# Modèle pour les témoignages clients spécifiques aux services
class TemoignageService(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='temoignages')
    texte = models.TextField()
    note = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])  # Note de 1 à 5
    date = models.DateField(auto_now_add=True)
    approuve = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Témoignage de {self.client.username} sur {self.service.nom}"


# ==================== MODÈLES POUR TECHNICIEN AGRONOME ====================

class FicheConseil(models.Model):
    """Fiche-conseil agricole créée par le technicien agronome"""
    titre = models.CharField(max_length=200)
    description = models.TextField()
    contenu = models.TextField(help_text="Contenu détaillé de la fiche-conseil")
    recommandations = models.TextField(help_text="Recommandations principales")
    periode_optimale = models.CharField(max_length=100, help_text="Période optimale pour l'application")
    difficulte = models.CharField(max_length=20, choices=[
        ('facile', 'Facile'),
        ('moyenne', 'Moyenne'),
        ('difficile', 'Difficile'),
    ], default='moyenne')
    
    # Relations
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fiches_conseils')
    culture = models.ForeignKey('Culture', on_delete=models.SET_NULL, null=True, blank=True, related_name='fiches_conseils')
    
    # Type et catégorie
    type_culture = models.CharField(max_length=50, choices=[
        ('cereales', 'Céréales'),
        ('legumes', 'Légumes'),
        ('fruits', 'Fruits'),
        ('racines', 'Racines et tubercules'),
        ('legumineuses', 'Légumineuses'),
        ('autre', 'Autre'),
    ], default='autre')
    categorie = models.CharField(max_length=50, choices=[
        ('plantation', 'Plantation'),
        ('entretien', 'Entretien'),
        ('recolte', 'Récolte'),
        ('traitement', 'Traitement'),
        ('fertilisation', 'Fertilisation'),
        ('irrigation', 'Irrigation'),
        ('autre', 'Autre'),
    ], default='autre')
    
    # Médias
    image = models.ImageField(upload_to='fiches_conseils/', null=True, blank=True)
    
    # Statut et suivi
    publie = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    telechargements = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Fiche-conseil"
        verbose_name_plural = "Fiches-conseils"
        ordering = ['-date_creation']
    
    def __str__(self):
        return self.titre


class PhotoCulture(models.Model):
    """Photo envoyée par un agriculteur pour suivi des cultures"""
    image = models.ImageField(upload_to='photos_cultures/')
    description = models.TextField(blank=True, help_text="Description de la photo")
    
    # Relations
    agriculteur = models.ForeignKey('Agriculteur', on_delete=models.CASCADE, related_name='photos')
    culture = models.ForeignKey('Culture', on_delete=models.SET_NULL, null=True, blank=True, related_name='photos')
    parcelle = models.ForeignKey('Parcelle', on_delete=models.SET_NULL, null=True, blank=True, related_name='photos')
    
    # Validation
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente de validation'),
        ('validee', 'Validée'),
        ('refusee', 'Refusée'),
    ], default='en_attente')
    validee_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='photos_validees')
    commentaire = models.TextField(blank=True, help_text="Commentaire du technicien")
    
    # Dates
    date_envoi = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Photo de culture"
        verbose_name_plural = "Photos de cultures"
        ordering = ['-date_envoi']
    
    def __str__(self):
        return f"Photo de {self.agriculteur.farm_name} - {self.date_envoi.strftime('%d/%m/%Y')}"

# ====== MODÈLES DE GESTION FINANCIÈRE ======

class CategorieDepense(models.Model):
    """Catégories de dépenses pour l'exploitation agricole"""
    nom = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    couleur = models.CharField(max_length=7, default="#007bff", help_text="Code couleur hexadécimal")
    
    class Meta:
        verbose_name = "Catégorie de dépense"
        verbose_name_plural = "Catégories de dépenses"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom

class CategorieRevenu(models.Model):
    """Catégories de revenus pour l'exploitation agricole"""
    nom = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    couleur = models.CharField(max_length=7, default="#28a745", help_text="Code couleur hexadécimal")
    
    class Meta:
        verbose_name = "Catégorie de revenu"
        verbose_name_plural = "Catégories de revenus"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom

class Depense(models.Model):
    """Modèle pour enregistrer les dépenses (intrants, main d'œuvre, carburant...)"""
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    categorie = models.ForeignKey(CategorieDepense, on_delete=models.SET_NULL, null=True, verbose_name="Catégorie")
    
    titre = models.CharField(max_length=200, verbose_name="Titre de la dépense")
    description = models.TextField(blank=True, null=True, verbose_name="Description détaillée")
    montant = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant (FCFA)")
    
    date_depense = models.DateField(verbose_name="Date de la dépense")
    date_enregistrement = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
    
    # Fournisseur/Facture
    fournisseur = models.CharField(max_length=200, blank=True, null=True, verbose_name="Fournisseur")
    numero_facture = models.CharField(max_length=100, blank=True, null=True, verbose_name="Numéro de facture")
    
    # Pièce jointe
    piece_jointe = models.FileField(upload_to='pieces_depenses/', blank=True, null=True, verbose_name="Pièce jointe")
    
    # Statut
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente de validation'),
        ('validee', 'Validée'),
        ('rejetee', 'Rejetée'),
    ], default='validee', verbose_name="Statut")
    
    class Meta:
        verbose_name = "Dépense"
        verbose_name_plural = "Dépenses"
        ordering = ['-date_depense']
    
    def __str__(self):
        return f"{self.titre} - {self.montant} FCFA"

class Revenu(models.Model):
    """Modèle pour enregistrer les revenus (ventes, location matériel...)"""
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    categorie = models.ForeignKey(CategorieRevenu, on_delete=models.SET_NULL, null=True, verbose_name="Catégorie")
    
    titre = models.CharField(max_length=200, verbose_name="Titre du revenu")
    description = models.TextField(blank=True, null=True, verbose_name="Description détaillée")
    montant = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant (FCFA)")
    
    date_revenu = models.DateField(verbose_name="Date du revenu")
    date_enregistrement = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
    
    # Client/Source
    client = models.CharField(max_length=200, blank=True, null=True, verbose_name="Client/Source")
    reference = models.CharField(max_length=100, blank=True, null=True, verbose_name="Référence")
    
    # Pièce jointe
    piece_jointe = models.FileField(upload_to='pieces_revenus/', blank=True, null=True, verbose_name="Pièce jointe")
    
    # Statut
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente de validation'),
        ('validee', 'Validée'),
        ('annulee', 'Annulée'),
    ], default='validee', verbose_name="Statut")
    
    class Meta:
        verbose_name = "Revenu"
        verbose_name_plural = "Revenus"
        ordering = ['-date_revenu']
    
    def __str__(self):
        return f"{self.titre} - {self.montant} FCFA"

class SoldeMensuel(models.Model):
    """Suivi des soldes mensuels"""
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    annee = models.IntegerField(verbose_name="Année")
    mois = models.IntegerField(verbose_name="Mois (1-12)")
    
    total_depenses = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total dépenses")
    total_revenus = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total revenus")
    solde = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Solde net")
    
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    
    class Meta:
        verbose_name = "Solde mensuel"
        verbose_name_plural = "Soldes mensuels"
        unique_together = ['utilisateur', 'annee', 'mois']
        ordering = ['-annee', '-mois']
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.mois}/{self.annee} - Solde: {self.solde} FCFA"
    
    def calculer_solde(self):
        """Calcule automatiquement le solde du mois"""
        from django.db.models import Sum
        
        # Calculer les dépenses du mois
        depenses = Depense.objects.filter(
            utilisateur=self.utilisateur,
            date_depense__year=self.annee,
            date_depense__month=self.mois,
            statut='validee'
        ).aggregate(total=Sum('montant'))['total'] or 0
        
        # Calculer les revenus du mois
        revenus = Revenu.objects.filter(
            utilisateur=self.utilisateur,
            date_revenu__year=self.annee,
            date_revenu__month=self.mois,
            statut='validee'
        ).aggregate(total=Sum('montant'))['total'] or 0
        
        self.total_depenses = depenses
        self.total_revenus = revenus
        self.solde = revenus - depenses
        self.save()

class Facture(models.Model):
    """Gestion des factures clients"""
    numero_facture = models.CharField(max_length=50, unique=True, verbose_name="Numéro de facture")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Client")
    
    date_emission = models.DateField(verbose_name="Date d'émission")
    date_echeance = models.DateField(verbose_name="Date d'échéance")
    date_reglement = models.DateField(blank=True, null=True, verbose_name="Date de règlement")
    
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant total")
    montant_regle = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant réglé")
    montant_restant = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant restant")
    
    # Statut
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente de paiement'),
        ('partiellement_payee', 'Partiellement payée'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
        ('en_retard', 'En retard'),
    ], default='en_attente', verbose_name="Statut")
    
    # Description
    description = models.TextField(verbose_name="Description des services/produits")
    
    # Fichier PDF
    fichier_pdf = models.FileField(upload_to='factures/', blank=True, null=True, verbose_name="Fichier PDF")
    
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-date_emission']
    
    def __str__(self):
        return f"Facture {self.numero_facture} - {self.client.nom}"
    
    def save(self, *args, **kwargs):
        # Calculer le montant restant
        self.montant_restant = self.montant_total - self.montant_regle
        
        # Mettre à jour le statut automatiquement
        if self.montant_regle <= 0:
            self.statut = 'en_attente'
        elif self.montant_regle >= self.montant_total:
            self.statut = 'payee'
            if not self.date_reglement:
                self.date_reglement = timezone.now().date()
        else:
            self.statut = 'partiellement_payee'
        
        # Vérifier si en retard
        if self.statut in ['en_attente', 'partiellement_payee'] and self.date_echeance < timezone.now().date():
            self.statut = 'en_retard'
        
        super().save(*args, **kwargs)

class PaiementClient(models.Model):
    """Suivi des paiements des clients"""
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='paiements')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Client")
    
    montant = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant payé")
    date_paiement = models.DateField(verbose_name="Date du paiement")
    
    methode_paiement = models.CharField(max_length=50, choices=[
        ('orange_money', 'Orange Money'),
        ('wave', 'Wave'),
        ('mtn_momo', 'MTN Mobile Money'),
        ('carte_bancaire', 'Carte bancaire'),
        ('especes', 'Espèces'),
        ('cheque', 'Chèque'),
        ('virement', 'Virement bancaire'),
    ], verbose_name="Méthode de paiement")
    
    reference_paiement = models.CharField(max_length=100, blank=True, null=True, verbose_name="Référence du paiement")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente de validation'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
    ], default='valide', verbose_name="Statut")
    
    date_enregistrement = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
    
    class Meta:
        verbose_name = "Paiement client"
        verbose_name_plural = "Paiements clients"
        ordering = ['-date_paiement']
    
    def __str__(self):
        return f"Paiement {self.montant} FCFA - {self.client.nom} - {self.facture.numero_facture}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Mettre à jour la facture associée
        self.facture.save()

class RapportFinancier(models.Model):
    """Rapports financiers générés"""
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    type_rapport = models.CharField(max_length=50, choices=[
        ('mensuel', 'Rapport mensuel'),
        ('trimestriel', 'Rapport trimestriel'),
        ('annuel', 'Rapport annuel'),
        ('personnalise', 'Rapport personnalisé'),
    ], verbose_name="Type de rapport")
    
    titre = models.CharField(max_length=200, verbose_name="Titre du rapport")
    periode_debut = models.DateField(verbose_name="Début de la période")
    periode_fin = models.DateField(verbose_name="Fin de la période")
    
    # Données du rapport
    total_depenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_revenus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    solde_net = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Fichiers générés
    fichier_pdf = models.FileField(upload_to='rapports_financiers/pdf/', blank=True, null=True)
    fichier_excel = models.FileField(upload_to='rapports_financiers/excel/', blank=True, null=True)
    
    date_generation = models.DateTimeField(auto_now_add=True, verbose_name="Date de génération")
    
    class Meta:
        verbose_name = "Rapport financier"
        verbose_name_plural = "Rapports financiers"
        ordering = ['-date_generation']
    
    def __str__(self):
        return f"{self.titre} - {self.periode_debut} au {self.periode_fin}"
