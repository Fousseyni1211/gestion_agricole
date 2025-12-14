from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.http import JsonResponse

def debug_agriculteurs(request):
    User = get_user_model()
    agriculteurs = User.objects.filter(role__iexact='Agriculteur').values('id', 'first_name', 'last_name', 'gender', 'is_active')
    
    # Compter les genres
    stats = {
        'male': User.objects.filter(role__iexact='Agriculteur', gender='M').count(),
        'female': User.objects.filter(role__iexact='Agriculteur', gender='F').count(),
        'other': User.objects.filter(role__iexact='Agriculteur').exclude(gender__in=['M', 'F']).count(),
        'total': agriculteurs.count()
    }
    
    return JsonResponse({
        'agriculteurs': list(agriculteurs),
        'stats': stats
    })
