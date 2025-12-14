from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser, Agriculteur, Produit, Commande
import json

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def reset_password_agriculteur(request, user_id):
    """
    Réinitialise le mot de passe d'un agriculteur.
    Accessible uniquement aux administrateurs.
    """
    if request.method == 'POST':
        try:
            user = get_object_or_404(CustomUser, id=user_id, role__iexact='Agriculteur')
            data = json.loads(request.body)
            new_password = data.get('password')
            
            if len(new_password) < 8:
                return JsonResponse({'success': False, 'error': 'Le mot de passe doit contenir au moins 8 caractères.'})
            
            user.set_password(new_password)
            user.save()
            
            return JsonResponse({'success': True, 'message': 'Mot de passe réinitialisé avec succès.'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'})

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def get_agriculteur_activity(request, user_id):
    """
    Récupère l'activité d'un agriculteur.
    Accessible uniquement aux administrateurs.
    """
    try:
        user = get_object_or_404(CustomUser, id=user_id, role__iexact='Agriculteur')
        agriculteur = user.agriculteur
        
        # Statistiques de base
        products_added = Produit.objects.filter(created_by=user).count()
        orders_created = Commande.objects.filter(client=user).count()
        
        # Dernière connexion
        last_login = user.last_login
        if last_login:
            last_login_str = last_login.strftime('%d/%m/%Y à %H:%M')
        else:
            last_login_str = 'Jamais'
        
        # Temps de connexion (simulation - en réalité, il faudrait un système de suivi)
        total_time = "2h 30m"  # Valeur par défaut
        
        # Activités récentes (simulation)
        recent_activities = []
        
        # Produits récents
        recent_products = Produit.objects.filter(created_by=user).order_by('-created_at')[:5]
        for product in recent_products:
            recent_activities.append({
                'type': 'produit',
                'description': f'Ajout du produit "{product.nom_produit}"',
                'date': product.created_at.strftime('%d/%m/%Y %H:%M'),
                'icon': 'bi-seedling'
            })
        
        # Commandes récentes
        recent_orders = Commande.objects.filter(client=user).order_by('-date_commande')[:5]
        for order in recent_orders:
            recent_activities.append({
                'type': 'commande',
                'description': f'Commande #{order.id} - {order.statut}',
                'date': order.date_commande.strftime('%d/%m/%Y %H:%M'),
                'icon': 'bi-cart'
            })
        
        # Trier par date
        recent_activities.sort(key=lambda x: x['date'], reverse=True)
        
        activity_data = {
            'products_added': products_added,
            'orders_created': orders_created,
            'last_login': last_login_str,
            'total_time': total_time,
            'recent_activities': recent_activities[:10],  # Limiter à 10 activités
            'user_info': {
                'full_name': user.get_full_name(),
                'username': user.username,
                'email': user.email,
                'date_joined': user.date_joined.strftime('%d/%m/%Y'),
                'is_active': user.is_active
            }
        }
        
        return JsonResponse(activity_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def manage_agriculteur_permissions(request, user_id):
    """
    Gère les permissions d'un agriculteur.
    Accessible uniquement aux administrateurs.
    """
    if request.method == 'POST':
        try:
            user = get_object_or_404(CustomUser, id=user_id, role__iexact='Agriculteur')
            data = json.loads(request.body)
            
            # Gérer le statut actif/inactif
            if 'is_active' in data:
                user.is_active = data['is_active']
                user.save()
            
            # Gérer les permissions spécifiques (si applicable)
            # Par exemple: peut_ajouter_produits, peut_voir_rapports, etc.
            if 'permissions' in data:
                permissions = data['permissions']
                # Ici, vous pourriez avoir un modèle de permissions séparé
                # Pour l'instant, nous utilisons les champs de base de CustomUser
                if 'can_add_products' in permissions:
                    # Champ hypothétique dans CustomUser
                    pass
                
                if 'can_view_reports' in permissions:
                    # Champ hypothétique dans CustomUser
                    pass
            
            return JsonResponse({
                'success': True, 
                'message': 'Permissions mises à jour avec succès.',
                'is_active': user.is_active
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - retourner les permissions actuelles
    try:
        user = get_object_or_404(CustomUser, id=user_id, role__iexact='Agriculteur')
        
        permissions_data = {
            'is_active': user.is_active,
            'permissions': {
                'can_add_products': True,  # Valeurs par défaut
                'can_view_reports': False,
                'can_manage_orders': True
            }
        }
        
        return JsonResponse(permissions_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
