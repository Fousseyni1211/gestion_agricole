from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings

def envoyer_alerte_stock(produit):
    sujet = f"Alerte stock faible: {produit.nom_produit}"
    message = (
        f"Le stock du produit '{produit.nom_produit}' est bas.\n"
        f"Quantité actuelle: {produit.stock.quantite}\n"
        f"Seuil d'alerte: {produit.seuil_alerte}\n"
        "Merci de prévoir un réapprovisionnement rapidement."
    )
    send_mail(
        sujet,
        message,
        settings.DEFAULT_FROM_EMAIL,
        settings.ADMIN_EMAILS,
        fail_silently=False,
    )


def envoyer_notification_commande_admin(commande):
    """
    Envoie une notification par email au client lorsqu'un gérant crée une commande.
    La commande est automatiquement validée.
    """
    try:
        client = commande.client
        if not client.email:
            return False
            
        # Préparer le contenu de l'email
        subject = f"🎉 Commande #{commande.id} validée - FAMA"
        
        # Construire le message HTML
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Commande Validée - FAMA</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .email-container {{
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #10b981;
                }}
                .logo {{
                    font-size: 2rem;
                    font-weight: bold;
                    color: #10b981;
                    margin-bottom: 10px;
                }}
                .subtitle {{
                    color: #666;
                    font-size: 1.1rem;
                }}
                .success-badge {{
                    background: linear-gradient(135deg, #10b981, #059669);
                    color: white;
                    padding: 10px 20px;
                    border-radius: 25px;
                    display: inline-block;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .order-details {{
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .order-info {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                    padding: 8px 0;
                    border-bottom: 1px solid #e9ecef;
                }}
                .order-info:last-child {{
                    border-bottom: none;
                    font-weight: bold;
                    font-size: 1.1rem;
                    color: #10b981;
                }}
                .products-list {{
                    margin: 20px 0;
                }}
                .product-item {{
                    background-color: #ffffff;
                    border: 1px solid #e9ecef;
                    border-radius: 6px;
                    padding: 15px;
                    margin-bottom: 10px;
                }}
                .product-name {{
                    font-weight: bold;
                    color: #10b981;
                }}
                .product-details {{
                    color: #666;
                    font-size: 0.9rem;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e9ecef;
                    color: #666;
                    font-size: 0.9rem;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <div class="logo">🌱 FAMA</div>
                    <div class="subtitle">Ferme Agricole pour la Meilleure Alimentation</div>
                </div>
                
                <h2>Bonjour {client.get_full_name() or client.username},</h2>
                
                <p>Nous avons le plaisir de vous informer qu'une nouvelle commande a été créée et <strong>validée automatiquement</strong> par notre équipe.</p>
                
                <div class="success-badge">
                    ✅ Commande #{commande.id} - VALIDÉE
                </div>
                
                <div class="order-details">
                    <h3>📋 Détails de votre commande</h3>
                    
                    <div class="order-info">
                        <span>Numéro de commande:</span>
                        <span>#{commande.id}</span>
                    </div>
                    
                    <div class="order-info">
                        <span>Date de création:</span>
                        <span>{commande.date_commande.strftime('%d/%m/%Y à %H:%M')}</span>
                    </div>
                    
                    <div class="order-info">
                        <span>Statut:</span>
                        <span style="color: #10b981; font-weight: bold;">Validée</span>
                    </div>
                    
                    <div class="order-info">
                        <span>Total:</span>
                        <span>{commande.total} FCFA</span>
                    </div>
                </div>
                
                <div class="products-list">
                    <h3>🛒 Produits commandés</h3>
                    {''.join([f'''
                    <div class="product-item">
                        <div class="product-name">{detail.produit.nom_produit}</div>
                        <div class="product-details">
                            Quantité: {detail.quantite} | 
                            Prix unitaire: {detail.prix_unitaire} FCFA | 
                            Sous-total: {detail.quantite * detail.prix_unitaire} FCFA
                        </div>
                    </div>
                    ''' for detail in commande.details.all()])}
                </div>
                
                <p><strong>🎯 Votre commande est maintenant en cours de traitement et sera expédiée dans les plus brefs délais.</strong></p>
                
                <p>Vous recevrez prochainement un email de suivi avec les informations de livraison.</p>
                
                <div style="text-align: center;">
                    <a href="#" class="cta-button">Suivre ma commande</a>
                </div>
                
                <div class="footer">
                    <p>Merci de votre confiance en FAMA !</p>
                    <p>Pour toute question, contactez-nous à support@fama.ag</p>
                    <p>© 2024 FAMA - Tous droits réservés</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Message texte simple pour les clients qui ne supportent pas HTML
        text_message = f"""
        Bonjour {client.get_full_name() or client.username},

        Nous avons le plaisir de vous informer qu'une nouvelle commande a été créée et validée automatiquement par notre équipe.

        Commande #{commande.id} - VALIDÉE
        Date: {commande.date_commande.strftime('%d/%m/%Y à %H:%M')}
        Total: {commande.total} FCFA

        Produits commandés:
        {chr(10).join([f'- {detail.produit.nom_produit} (x{detail.quantite}) - {detail.quantite * detail.prix_unitaire} FCFA' for detail in commande.details.all()])}

        Votre commande est maintenant en cours de traitement et sera expédiée dans les plus brefs délais.

        Merci de votre confiance en FAMA !
        Pour toute question, contactez-nous à support@fama.ag
        """
        
        # Créer l'email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email='noreply@fama.ag',
            to=[client.email]
        )
        
        # Ajouter la version HTML
        email.attach_alternative(html_message, "text/html")
        
        # Envoyer l'email
        email.send()
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de notification: {str(e)}")
        return False
