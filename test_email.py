#!/usr/bin/env python
"""Script de test pour la configuration email Django"""

import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_agricole.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=== Test de configuration email Django ===")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print()

# Vérifier si les identifiants sont configurés
if not settings.EMAIL_HOST_USER:
    print("❌ ERREUR: EMAIL_HOST_USER n'est pas défini!")
    print("   Définissez la variable d'environnement EMAIL_HOST_USER")
    sys.exit(1)

if not settings.EMAIL_HOST_PASSWORD:
    print("❌ ERREUR: EMAIL_HOST_PASSWORD n'est pas défini!")
    print("   Définissez la variable d'environnement EMAIL_HOST_PASSWORD")
    sys.exit(1)

print("✅ Configuration email semble complète")
print()

# Test d'envoi d'email
try:
    print("📧 Envoi d'un email de test...")
    result = send_mail(
        'Test Email - Kayupe Agriculture',
        'Ceci est un email de test pour vérifier la configuration SMTP.',
        settings.DEFAULT_FROM_EMAIL,
        [settings.DEFAULT_FROM_EMAIL],  # Envoyer à soi-même pour tester
        fail_silently=False,
    )
    
    if result == 1:
        print("✅ Email envoyé avec succès!")
    else:
        print("❌ Échec de l'envoi de l'email")
        
except Exception as e:
    print(f"❌ Erreur lors de l'envoi: {type(e).__name__}: {e}")
    print()
    print("Solutions possibles:")
    print("1. Vérifiez que le mot de passe d'application Gmail est correct")
    print("2. Activez l'authentification à deux facteurs sur Gmail")
    print("3. Générez un mot de passe d'application Gmail")
    print("4. Vérifiez que EMAIL_HOST_USER est l'adresse email complète")
