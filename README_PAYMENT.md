# 📱 Intégration Paiement Mobile - Orange Money, Moov Money, Wave

## 🌟 Vue d'ensemble

Système de paiement unifié pour les solutions mobiles africaines les plus populaires :
- **Orange Money** 🟠
- **Moov Money** 🟣  
- **Wave** 🌊

## 🚀 Fonctionnalités

- ✅ Interface de sélection de paiement moderne et responsive
- ✅ Support multi-fournisseurs avec API unifiée
- ✅ Gestion automatique des statuts de paiement
- ✅ Callbacks et webhooks pour mises à jour en temps réel
- ✅ Mode sandbox pour tests
- ✅ Interface mobile optimisée

## 📋 Prérequis

1. **Comptes développeurs** :
   - [Orange Developer Portal](https://developer.orange.com/)
   - [Moov Money API](https://moov-africa.com/)
   - [Wave API](https://wave.com/developers)

2. **Clés API** pour chaque fournisseur

## ⚙️ Configuration

### Variables d'environnement (Render)

```bash
# Mode de test (True) ou production (False)
PAYMENT_SANDBOX=True

# Orange Money
ORANGE_MONEY_API_KEY=votre_cle_api_orange
ORANGE_MONEY_API_SECRET=votre_secret_orange

# Moov Money
MOOV_MONEY_API_KEY=votre_cle_api_moov
MOOV_MONEY_API_SECRET=votre_secret_moov

# Wave
WAVE_API_KEY=votre_cle_api_wave
WAVE_API_SECRET=votre_secret_wave
```

### Configuration locale (.env)

```bash
PAYMENT_SANDBOX=True
ORANGE_MONEY_API_KEY=test_key_orange
ORANGE_MONEY_API_SECRET=test_secret_orange
MOOV_MONEY_API_KEY=test_key_moov
MOOV_MONEY_API_SECRET=test_secret_moov
WAVE_API_KEY=test_key_wave
WAVE_API_SECRET=test_secret_wave
```

## 🔄 Flux de paiement

1. **Sélection** : Client choisit son fournisseur de paiement
2. **Initiation** : Système crée la transaction auprès du fournisseur
3. **Redirection** : Client est redirigé vers la page de paiement du fournisseur
4. **Confirmation** : Webhook/callback met à jour le statut en base
5. **Finalisation** : Commande marquée comme payée

## 📱 Utilisation

### Pour le gérant

1. Aller dans la liste des commandes
2. Cliquer sur "Détails" d'une commande
3. Cliquer sur "Payer en ligne" 
4. Guider le client dans le processus de paiement

### Pour le client

1. Recevoir le lien de paiement (email/SMS)
2. Choisir sa méthode de paiement
3. Entrer son numéro de téléphone
4. Confirmer sur son application mobile

## 🛠️ Installation

1. **Déployer le code** :
```bash
git add -A
git commit -m "Add payment integration"
git push origin main
```

2. **Configurer les variables** sur Render
3. **Tester en mode sandbox** d'abord

## 🔧 Tests

### Mode Sandbox activé par défaut

Pour tester sans vrais paiements :
```python
# Les transactions sont simulées
# Aucun argent n'est débité
# Interface identique à la production
```

### Test manuel

1. Créer une commande test
2. Cliquer sur "Payer en ligne"
3. Choisir un fournisseur
4. Utiliser un numéro de test (ex: 0700000000)

## 📊 Statuts de paiement

| Statut | Description |
|--------|-------------|
| `en_attente` | Paiement initié, en attente de confirmation |
| `validé` | Paiement confirmé avec succès |
| `échoué` | Paiement refusé ou expiré |
| `annulé` | Paiement annulé par le client |

## 🚨 Dépannage

### Erreur "Fournisseur non supporté"
- Vérifier que le fournisseur est bien configuré dans `PaymentManager`
- Confirmer les clés API sont valides

### Erreur "Non autorisé"  
- Vérifier que l'utilisateur a les droits (staff/superuser)
- Confirmer que la commande appartient bien au client

### Callback non reçu
- Vérifier l'URL de callback est accessible
- Confirmer le webhook est configuré chez le fournisseur

## 📞 Support

Pour obtenir les clés API :

- **Orange Money** : contactez support.orange@orange.com
- **Moov Money** : support@moov-africa.com  
- **Wave** : developers@wave.com

## 🔐 Sécurité

- ✅ Token CSRF obligatoire
- ✅ Validation des numéros de téléphone
- ✅ HTTPS obligatoire en production
- ✅ Clés API chiffrées en base
- ✅ Logs de toutes les transactions

---

**Prochaines étapes** :
1. Obtenir les clés API des fournisseurs
2. Configurer les variables d'environnement
3. Tester en mode sandbox
4. Passer en production

*L'intégration est prête à utiliser ! 🚀*
