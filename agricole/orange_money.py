import os
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement du fichier .env
load_dotenv()

class OrangeMoneyAPI:
    BASE_URL = "https://api.orange.com/orange-money-webpay"
    TOKEN_URL = "https://api.orange.com/oauth/v3/token"

    def __init__(self):
        self.client_id = os.getenv("ORANGE_CLIENT_ID")
        self.client_secret = os.getenv("ORANGE_CLIENT_SECRET")
        self.merchant_key = os.getenv("ORANGE_MERCHANT_KEY")
        self.access_token = None

    def get_token(self):
        """Obtient un token d'authentification auprès de l'API Orange."""
        auth = (self.client_id, self.client_secret)
        data = {'grant_type': 'client_credentials'}
        try:
            response = requests.post(self.TOKEN_URL, auth=auth, data=data, timeout=30)
            response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
            self.access_token = response.json().get("access_token")
            return self.access_token
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de l'obtention du token: {e}")
            return None

    def initiate_payment(self, amount, order_id, return_url, cancel_url, notify_url):
        """Initialise une transaction de paiement."""
        if not self.access_token:
            self.get_token()
        
        if not self.access_token:
            return {'error': 'Impossible d\'obtenir le token d\'accès.'}

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "merchant_key": self.merchant_key,
            "currency": "XOF",  # Devise pour le Mali
            "order_id": order_id,
            "amount": amount,
            "return_url": return_url,
            "cancel_url": cancel_url,
            "notify_url": notify_url,
            "lang": "fr"
        }

        try:
            response = requests.post(f"{self.BASE_URL}/api/eWallet/v1/payments/", headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de l'initiation du paiement: {e}")
            return {'error': str(e)}
