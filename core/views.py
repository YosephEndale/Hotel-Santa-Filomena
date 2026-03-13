from django.shortcuts import render
from rooms.models import Room, RoomImage
from restaurant.models import MenuItem


def home(request):
    featured_rooms = Room.objects.filter(
        is_available=True, is_featured=True
    ).prefetch_related('images')[:3]
    return render(request, 'core/home.html', {'featured_rooms': featured_rooms})


def gallery(request):
    # All room images grouped by room
    room_images = RoomImage.objects.select_related('room').filter(
        room__is_available=True
    ).order_by('room__name', 'order')

    # Featured menu photos
    food_images = MenuItem.objects.filter(
        is_available=True,
        photo__isnull=False
    ).exclude(photo='').order_by('category', 'order')[:12]

    # Active filter from query param
    active_filter = request.GET.get('filter', 'all')

    context = {
        'room_images':   room_images,
        'food_images':   food_images,
        'active_filter': active_filter,
    }
    return render(request, 'core/gallery.html', context)