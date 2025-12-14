from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CategorieService(models.Model):
    """Catégorie de service (ex: Entretien, Réparation, Consultation)"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icone = models.CharField(max_length=50, default='fa-cogs',
                           help_text="Classe FontAwesome pour l'icône")
    couleur = models.CharField(max_length=20, default='#6c757d',
                             help_text="Code couleur hexadécimal")
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Catégorie de service")
        verbose_name_plural = _("Catégories de service")
        ordering = ['nom']

    def __str__(self):
        return self.nom

class Service(models.Model):
    """Service proposé par l'entreprise"""
    class StatutService(models.TextChoices):
        ACTIF = 'actif', _('Actif')
        INACTIF = 'inactif', _('Inactif')
        EN_MAINTENANCE = 'maintenance', _('En maintenance')

    nom = models.CharField(max_length=200)
    description = models.TextField()
    categorie = models.ForeignKey(CategorieService, on_delete=models.PROTECT, related_name='services')
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    duree_moyenne = models.PositiveIntegerField(help_text="Durée moyenne en minutes", default=60)
    statut = models.CharField(max_length=20, choices=StatutService.choices, default=StatutService.ACTIF)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    notes_internes = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ['categorie__nom', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.categorie})"

class DemandeService(models.Model):
    """Demande de service par un client"""
    class StatutDemande(models.TextChoices):
        NOUVELLE = 'nouvelle', _('Nouvelle')
        EN_COURS = 'en_cours', _('En cours')
        TERMINEE = 'terminee', _('Terminée')
        ANNULEE = 'annulee', _('Annulée')
        FACTUREE = 'facturee', _('Facturée')

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='demandes_service')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='demandes')
    description = models.TextField(help_text="Détails de la demande")
    statut = models.CharField(max_length=20, choices=StatutDemande.choices, default=StatutDemande.NOUVELLE)
    date_demande = models.DateTimeField(auto_now_add=True)
    date_prise_en_charge = models.DateTimeField(blank=True, null=True)
    date_fin = models.DateTimeField(blank=True, null=True)
    employe_attribue = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                       null=True, blank=True, 
                                       related_name='services_assignes')
    notes = models.TextField(blank=True, null=True, help_text="Notes internes")
    cout = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    facture = models.ForeignKey('Facture', on_delete=models.SET_NULL, 
                               null=True, blank=True, 
                               related_name='services_factures')

    class Meta:
        verbose_name = _("Demande de service")
        verbose_name_plural = _("Demandes de service")
        ordering = ['-date_demande']

    def __str__(self):
        return f"{self.client.get_full_name()} - {self.service.nom} ({self.get_statut_display()})"

class Intervention(models.Model):
    """Suivi des interventions pour une demande de service"""
    demande = models.ForeignKey(DemandeService, on_delete=models.CASCADE, related_name='interventions')
    technicien = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='interventions')
    date_intervention = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    duree = models.PositiveIntegerField(help_text="Durée en minutes", default=0)
    cout_materiel = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cout_main_oeuvre = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Intervention")
        verbose_name_plural = _("Interventions")
        ordering = ['-date_intervention']

    def __str__(self):
        return f"Intervention du {self.date_intervention} pour {self.demande}"

class Facture(models.Model):
    """Facture pour les services rendus"""
    class StatutFacture(models.TextChoices):
        BROUILLON = 'brouillon', _('Brouillon')
        EMISE = 'emise', _('Emise')
        PAYEE = 'payee', _('Payée')
        EN_RETARD = 'retard', _('En retard')
        ANNULEE = 'annulee', _('Annulée')

    numero = models.CharField(max_length=20, unique=True)
    client = models.ForeignKey(User, on_delete=models.PROTECT, related_name='factures_service')
    date_emission = models.DateField()
    date_echeance = models.DateField()
    statut = models.CharField(max_length=20, choices=StatutFacture.choices, default=StatutFacture.BROUILLON)
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=18.0)
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)
    mode_paiement = models.CharField(max_length=50, blank=True, null=True)
    date_paiement = models.DateField(blank=True, null=True)
    reference_paiement = models.CharField(max_length=100, blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='factures_creees')

    class Meta:
        verbose_name = _("Facture de service")
        verbose_name_plural = _("Factures de service")
        ordering = ['-date_emission', '-numero']

    def __str__(self):
        return f"Facture {self.numero} - {self.client.get_full_name()}"

    def calculer_montants(self):
        """Calcule les montants HT et TTC"""
        montant_ht = sum(ligne.montant for ligne in self.lignes.all())
        self.montant_ht = montant_ht
        self.montant_ttc = montant_ht * (1 + self.tva / 100)
        self.save()

class LigneFactureService(models.Model):
    """Ligne de facture pour les services"""
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    demande_service = models.OneToOneField(DemandeService, on_delete=models.PROTECT, 
                                         related_name='ligne_facture')
    description = models.TextField()
    quantite = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=18.0)
    montant = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        verbose_name = _("Ligne de facture de service")
        verbose_name_plural = _("Lignes de facture de service")

    def save(self, *args, **kwargs):
        self.montant = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)
        self.facture.calculer_montants()

    def __str__(self):
        return f"{self.description} - {self.montant} FCFA"
