#!/usr/bin/env python
import os
import sys
import django

# Configurer Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_agricole.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_configuration():
    print("🔍 TEST DE CONFIGURATION EMAIL")
    print("=" * 50)
    
    # Afficher la configuration
    print(f"📧 EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"🌐 EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"🔌 EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"🔒 EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"👤 EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"📨 DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # Vérifier le mot de passe
    if not hasattr(settings, 'EMAIL_HOST_PASSWORD') or settings.EMAIL_HOST_PASSWORD == 'ENTREZ_VOTRE_MOT_DE_PASSE_GMAIL_ICI':
        print("\n❌ ERREUR CRITIQUE!")
        print("   Le mot de passe Gmail n'est pas configuré!")
        print("   EMAIL_HOST_PASSWORD est toujours: 'ENTREZ_VOTRE_MOT_DE_PASSE_GMAIL_ICI'")
        return False
    
    if settings.EMAIL_HOST_PASSWORD:
        masked_password = settings.EMAIL_HOST_PASSWORD[:4] + '*' * (len(settings.EMAIL_HOST_PASSWORD) - 4) if len(settings.EMAIL_HOST_PASSWORD) > 4 else '****'
        print(f"🔐 EMAIL_HOST_PASSWORD: {masked_password}")
    else:
        print("\n❌ ERREUR: EMAIL_HOST_PASSWORD est vide!")
        return False
    
    print("\n📤 TEST D'ENVOI D'EMAIL...")
    print("=" * 50)
    
    try:
        result = send_mail(
            '🧪 Test Email - Kayupe Agriculture',
            'Ceci est un email de test pour vérifier que la configuration SMTP fonctionne correctement.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER],  # Envoyer à soi-même pour tester
            fail_silently=False,
        )
        
        if result == 1:
            print("✅ SUCCÈS! Email envoyé correctement!")
            print(f"   Vérifiez votre boîte de réception: {settings.EMAIL_HOST_USER}")
            return True
        else:
            print(f"❌ ÉCHEC: send_mail a retourné {result}")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR lors de l'envoi: {str(e)}")
        print("\n🔧 SOLUTIONS POSSIBLES:")
        print("1. Vérifiez que le mot de passe Gmail est correct")
        print("2. Activez 'Accès moins sécurisé aux applications' dans Gmail")
        print("3. Utilisez un 'Mot de passe d'application' Gmail (recommandé)")
        print("4. Vérifiez que EMAIL_HOST_USER est l'adresse email complète")
        return False

if __name__ == '__main__':
    success = test_email_configuration()
    
    if not success:
        print("\n" + "=" * 50)
        print("📋 INSTRUCTIONS POUR CORRIGER:")
        print("=" * 50)
        print("1. Allez dans votre compte Gmail")
        print("2. Activez la vérification en deux étapes")
        print("3. Générez un 'Mot de passe d'application':")
        print("   - https://myaccount.google.com/apppasswords")
        print("   - Sélectionnez 'Autre' et donnez un nom")
        print("   - Copiez le mot de passe de 16 caractères")
        print("4. Définissez la variable d'environnement:")
        print(f"   set EMAIL_HOST_PASSWORD=votre_mot_de_passe_16_caracteres")
        print("5. Relancez le serveur Django")
        print("=" * 50)
    
    sys.exit(0 if success else 1)
