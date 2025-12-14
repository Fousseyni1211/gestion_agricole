from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Notification, CustomUser

@login_required
@require_http_methods(["POST"])
def mark_notification_as_read(request, notification_id):
    """Marque une notification comme lue"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success', 
                'unread_count': Notification.get_unread_count(request.user)
            })
        
        messages.success(request, 'Notification marquée comme lue')
        return redirect(notification.url) if notification.url else redirect('admin_home')
    except Notification.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Notification non trouvée'}, status=404)
        messages.error(request, 'Notification non trouvée')
        return redirect('gerant_home')

@login_required
@require_http_methods(["POST"])
def mark_all_notifications_as_read(request):
    """Marque toutes les notifications de l'utilisateur comme lues"""
    updated = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).update(is_read=True, updated_at=timezone.now())
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'{updated} notifications marquées comme lues',
            'unread_count': 0
        })
    
    messages.success(request, f'{updated} notifications ont été marquées comme lues')
    return redirect(request.META.get('HTTP_REFERER', 'gerant_home'))

@login_required
@require_http_methods(["POST"])
def delete_notification(request, notification_id):
    """Supprime une notification"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Notification supprimée avec succès',
                'unread_count': Notification.get_unread_count(request.user)
            })
        
        messages.success(request, 'Notification supprimée avec succès')
        return redirect(request.META.get('HTTP_REFERER', 'gerant_home'))
    except Notification.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Notification non trouvée'}, status=404)
        messages.error(request, 'Notification non trouvée')
        return redirect('gerant_home')

@login_required
def get_notifications(request):
    """Renvoie les notifications non lues au format JSON (pour les requêtes AJAX)"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'message': 'Requête non autorisée'}, status=400)
    
    try:
        # Récupérer les 10 dernières notifications non lues
        notifications = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).order_by('-created_at')[:10]
        
        # Préparer les données pour la réponse JSON
        notifications_data = [{
            'id': n.id,
            'message': n.message,
            'type': n.type,
            'icon': n.get_icon_class(),
            'url': n.get_absolute_url(),
            'created_at': n.created_at.strftime('%d/%m/%Y %H:%M'),
            'time_ago': n.get_time_ago(),
            'is_read': n.is_read
        } for n in notifications]
        
        return JsonResponse({
            'status': 'success',
            'notifications': notifications_data,
            'unread_count': Notification.get_unread_count(request.user)
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def notification_list(request):
    """Affiche la liste de toutes les notifications de l'utilisateur"""
    # Récupérer toutes les notifications de l'utilisateur, les plus récentes en premier
    notifications_list = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination - 15 notifications par page
    paginator = Paginator(notifications_list, 15)
    page = request.GET.get('page', 1)
    
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        # Si le paramètre page n'est pas un entier, afficher la première page
        notifications = paginator.page(1)
    except EmptyPage:
        # Si la page est hors de portée (trop grand), afficher la dernière page
        notifications = paginator.page(paginator.num_pages)
    
    # Marquer toutes les notifications comme lues lors de l'affichage de la première page
    if request.method == 'GET' and (page == '1' or not page):
        Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True, 
            updated_at=timezone.now()
        )
    
    # Préparer le contexte pour le template
    context = {
        'notifications': notifications,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': notifications,  # Pour la pagination dans le template
        'unread_count': 0,  # Toutes les notifications sont marquées comme lues
    }
    
    return render(request, 'admin/notifications/list.html', context)

@login_required
@require_http_methods(["POST"])
def delete_all_notifications(request):
    """Supprime toutes les notifications de l'utilisateur"""
    try:
        # Compter le nombre de notifications avant suppression
        count = Notification.objects.filter(user=request.user).count()
        
        # Supprimer toutes les notifications
        deleted_count, _ = Notification.objects.filter(user=request.user).delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'{deleted_count} notifications supprimées',
                'unread_count': 0
            })
            
        messages.success(request, f'{deleted_count} notifications ont été supprimées')
        return redirect('notification_list')
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
        messages.error(request, f'Erreur lors de la suppression des notifications: {str(e)}')
        return redirect('notification_list')

# Vue utilitaire pour créer des notifications de test (à supprimer en production)
@login_required
def create_test_notification(request):
    """Crée une notification de test (à des fins de débogage)"""
    if not request.user.is_superuser:
        messages.error(request, 'Accès refusé')
        return redirect('admin_home')
        
    notification_types = ['info', 'success', 'warning', 'danger']
    import random
    
    notification = Notification.create_notification(
        user=request.user,
        message=f'Ceci est une notification de test {random.randint(1, 100)}',
        notification_type=random.choice(notification_types),
        url=reverse('admin_home'),
        icon=Notification.get_default_icon(random.choice(notification_types))
    )
    
    messages.success(request, f'Notification de test créée avec succès (ID: {notification.id})')
    return redirect('notification_list')
