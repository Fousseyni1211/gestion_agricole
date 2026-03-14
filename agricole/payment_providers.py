"""
Intégration des fournisseurs de paiement africains
Orange Money, Moov Money, Wave
"""

import requests
import json
import hashlib
import hmac
import uuid
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from .models import Commande, Paiement

class BasePaymentProvider:
    """Classe de base pour tous les fournisseurs de paiement"""
    
    def __init__(self, api_key, api_secret, sandbox=True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.sandbox = sandbox
        self.base_url = self.get_base_url()
    
    def get_base_url(self):
        raise NotImplementedError
    
    def generate_transaction_id(self):
        return f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"
    
    def initiate_payment(self, amount, phone_number, description, callback_url):
        raise NotImplementedError
    
    def check_payment_status(self, transaction_id):
        raise NotImplementedError

class OrangeMoneyProvider(BasePaymentProvider):
    """Intégration Orange Money"""
    
    def get_base_url(self):
        if self.sandbox:
            return "https://api.orange.com/orange-money-api/sandbox"
        return "https://api.orange.com/orange-money-api"
    
    def get_access_token(self):
        """Obtenir le token d'accès OAuth2"""
        auth_url = f"{self.base_url}/token"
        headers = {
            'Authorization': f'Basic {self.generate_basic_auth()}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = 'grant_type=client_credentials'
        
        response = requests.post(auth_url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json().get('access_token')
        return None
    
    def generate_basic_auth(self):
        import base64
        credentials = f"{self.api_key}:{self.api_secret}"
        return base64.b64encode(credentials.encode()).decode()
    
    def initiate_payment(self, amount, phone_number, description, callback_url):
        token = self.get_access_token()
        if not token:
            return {'success': False, 'error': 'Impossible d\'obtenir le token d\'accès'}
        
        payment_url = f"{self.base_url}/payment"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        transaction_id = self.generate_transaction_id()
        data = {
            'merchant_key': self.api_key,
            'currency': 'XOF',  # Franc CFA
            'order_id': transaction_id,
            'amount': int(amount),
            'return_url': callback_url,
            'cancel_url': callback_url,
            'notif_url': callback_url,
            'description': description,
            'customer_phone_number': phone_number
        }
        
        try:
            response = requests.post(payment_url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'payment_url': result.get('payment_url'),
                    'provider': 'orange_money'
                }
            else:
                return {'success': False, 'error': f'Erreur API: {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class MoovMoneyProvider(BasePaymentProvider):
    """Intégration Moov Money"""
    
    def get_base_url(self):
        if self.sandbox:
            return "https://sandbox.moov.africa/api"
        return "https://api.moov.africa/api"
    
    def initiate_payment(self, amount, phone_number, description, callback_url):
        transaction_id = self.generate_transaction_id()
        payment_url = f"{self.base_url}/collection"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'transaction_id': transaction_id,
            'amount': int(amount),
            'currency': 'XOF',
            'description': description,
            'customer_number': phone_number,
            'callback_url': callback_url,
            'merchant_id': self.api_key
        }
        
        try:
            response = requests.post(payment_url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'payment_url': result.get('payment_url'),
                    'provider': 'moov_money'
                }
            else:
                return {'success': False, 'error': f'Erreur API: {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class WaveProvider(BasePaymentProvider):
    """Intégration Wave (Senegal, Côte d'Ivoire, etc.)"""
    
    def get_base_url(self):
        if self.sandbox:
            return "https://api.wave.com/v1/sandbox"
        return "https://api.wave.com/v1"
    
    def initiate_payment(self, amount, phone_number, description, callback_url):
        transaction_id = self.generate_transaction_id()
        payment_url = f"{self.base_url}/checkout/create"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'amount': int(amount * 100),  # Wave utilise les centimes
            'currency': 'XOF',
            'client_reference': transaction_id,
            'description': description,
            'redirect_url': callback_url,
            'mobile_money': {
                'phone_number': phone_number,
                'country': 'CI'  # Côte d'Ivoire, modifier selon pays
            }
        }
        
        try:
            response = requests.post(payment_url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'payment_url': result.get('checkout_url'),
                    'provider': 'wave'
                }
            else:
                return {'success': False, 'error': f'Erreur API: {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class PaymentManager:
    """Gestionnaire unifié pour tous les paiements"""
    
    def __init__(self):
        self.providers = {
            'orange_money': OrangeMoneyProvider(
                api_key=getattr(settings, 'ORANGE_MONEY_API_KEY', ''),
                api_secret=getattr(settings, 'ORANGE_MONEY_API_SECRET', ''),
                sandbox=getattr(settings, 'PAYMENT_SANDBOX', True)
            ),
            'moov_money': MoovMoneyProvider(
                api_key=getattr(settings, 'MOOV_MONEY_API_KEY', ''),
                api_secret=getattr(settings, 'MOOV_MONEY_API_SECRET', ''),
                sandbox=getattr(settings, 'PAYMENT_SANDBOX', True)
            ),
            'wave': WaveProvider(
                api_key=getattr(settings, 'WAVE_API_KEY', ''),
                api_secret=getattr(settings, 'WAVE_API_SECRET', ''),
                sandbox=getattr(settings, 'PAYMENT_SANDBOX', True)
            )
        }
    
    def initiate_payment(self, provider_name, amount, phone_number, description, callback_url, commande_id):
        """Lancer un paiement avec le fournisseur spécifié"""
        if provider_name not in self.providers:
            return {'success': False, 'error': 'Fournisseur non supporté'}
        
        provider = self.providers[provider_name]
        result = provider.initiate_payment(amount, phone_number, description, callback_url)
        
        if result['success']:
            # Sauvegarder la transaction en base
            paiement = Paiement.objects.create(
                commande_id=commande_id,
                montant=amount,
                methode_paiement=provider_name,
                reference_transaction=result['transaction_id'],
                statut='en_attente',
                date_paiement=timezone.now()
            )
            result['paiement_id'] = paiement.id
        
        return result
    
    def verify_payment(self, provider_name, transaction_id):
        """Vérifier le statut d'un paiement"""
        if provider_name not in self.providers:
            return {'success': False, 'error': 'Fournisseur non supporté'}
        
        provider = self.providers[provider_name]
        return provider.check_payment_status(transaction_id)
