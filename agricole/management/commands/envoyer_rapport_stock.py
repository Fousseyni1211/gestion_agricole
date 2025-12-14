from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from agricole.models import Produit  # adapte selon ton app

class Command(BaseCommand):
    help = 'Envoie un rapport PDF des stocks par email aux gérants'

    def handle(self, *args, **options):
        # Générer le PDF en mémoire
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50
        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, y, "Rapport Stocks")
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Produit")
        c.drawString(200, y, "Catégorie")
        c.drawString(350, y, "Quantité")
        c.drawString(450, y, "Seuil Alerte")
        y -= 20
        c.setFont("Helvetica", 12)

        produits = Produit.objects.all()
        for produit in produits:
            quantite = produit.stock.quantite if hasattr(produit, 'stock') else 0
            c.drawString(50, y, produit.nom)
            c.drawString(200, y, produit.categorie)
            c.drawString(350, y, str(quantite))
            c.drawString(450, y, str(produit.seuil_alerte))
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50
        c.save()
        buffer.seek(0)

        # Préparer l'email
        sujet = "Rapport hebdomadaire des stocks"
        corps = "Veuillez trouver ci-joint le rapport hebdomadaire des stocks."
        email = EmailMessage(
            sujet,
            corps,
            'no-reply@tonsite.com',
            ['admin@example.com'],  # adapte ici
        )
        email.attach('rapport_stocks.pdf', buffer.read(), 'application/pdf')
        email.send()

        self.stdout.write(self.style.SUCCESS('Rapport de stock envoyé avec succès.'))
