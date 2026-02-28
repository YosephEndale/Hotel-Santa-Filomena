from django.shortcuts import render
from rooms.models import Room


def home(request):
    featured_rooms = Room.objects.filter(
        is_available=True,
        is_featured=True
    ).prefetch_related('images')[:3]

    context = {
        'featured_rooms': featured_rooms,
    }
    return render(request, 'core/home.html', context)