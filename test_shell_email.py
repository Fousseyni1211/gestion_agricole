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

print("🔍 TEST DE CONFIGURATION EMAIL DANS SHELL DJANGO")
print("=" * 60)

try:
    print(f'📧 EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
    print(f'🌐 EMAIL_HOST: {settings.EMAIL_HOST}')
    print(f'👤 EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
    
    if hasattr(settings, 'EMAIL_HOST_PASSWORD'):
        masked = settings.EMAIL_HOST_PASSWORD[:4] + '*' * (len(settings.EMAIL_HOST_PASSWORD) - 8) + settings.EMAIL_HOST_PASSWORD[-4:] if len(settings.EMAIL_HOST_PASSWORD) > 8 else '****'
        print(f'🔐 EMAIL_HOST_PASSWORD: {masked}')
    else:
        print('❌ EMAIL_HOST_PASSWORD non défini')
    
    print("\n📤 TEST D'ENVOI D'EMAIL...")
    
    result = send_mail(
        '🧪 Test Email Django Shell',
        'Ceci est un test depuis le shell Django pour vérifier la configuration email.',
        settings.DEFAULT_FROM_EMAIL,
        [settings.EMAIL_HOST_USER],
        fail_silently=False,
    )
    
    if result == 1:
        print("✅ SUCCÈS! Email envoyé correctement depuis Django shell!")
        print(f"   Vérifiez votre boîte: {settings.EMAIL_HOST_USER}")
    else:
        print(f"❌ ÉCHEC: send_mail a retourné {result}")
        
except Exception as e:
    print(f"❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
