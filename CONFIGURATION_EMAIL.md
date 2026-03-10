# Configuration Email Gmail pour Kayupe Agriculture

## Problème identifié
Les emails n'étaient pas envoyés car `EMAIL_BACKEND` était configuré sur `console` au lieu de `smtp`.

## Solution appliquée
✅ Changement de `console.EmailBackend` vers `smtp.EmailBackend`
✅ Ajout de valeurs par défaut pour les identifiants

## Configuration requise pour Gmail

### 1. Activer l'authentification à deux facteurs sur Gmail
- Allez dans les paramètres de votre compte Google
- Section "Sécurité"
- Activez "Authentification à deux facteurs"

### 2. Générer un mot de passe d'application
- Allez sur https://myaccount.google.com/apppasswords
- Sélectionnez "Autre" comme application
- Donnez un nom (ex: "Kayupe Agriculture")
- Copiez le mot de passe généré (16 caractères)

### 3. Configurer les variables d'environnement

#### Option A: Variables d'environnement Windows
```cmd
set EMAIL_HOST_USER=fousseynimoussaberthe@gmail.com
set EMAIL_HOST_PASSWORD=votre_mot_de_passe_application_16_caracteres
```

#### Option B: Modifier directement settings.py (développement uniquement)
Dans `gestion_agricole/settings.py`, ligne 30:
```python
EMAIL_HOST_PASSWORD = 'votre_mot_de_passe_application_16_caracteres'
```

### 4. Redémarrer le serveur Django
```cmd
python manage.py runserver
```

## Test de la configuration
Exécutez le script de test:
```cmd
python test_email.py
```

## Déploiement sur Render
Sur Render, configurez les variables d'environnement dans le dashboard:
- `EMAIL_HOST_USER`: fousseynimoussaberthe@gmail.com
- `EMAIL_HOST_PASSWORD`: votre_mot_de_passe_application

## Sécurité
⚠️ N'utilisez JAMAIS votre mot de passe Gmail normal!
⚠️ Utilisez TOUJOURS un mot de passe d'application!
⚠️ Ne commitez JAMAIS les mots de passe dans Git!

## Dépannage
- Si erreur SMTP: vérifiez le mot de passe d'application
- Si email dans spam: configurez SPF/DKIM (avancé)
- Si timeout: vérifiez firewall/port 587
