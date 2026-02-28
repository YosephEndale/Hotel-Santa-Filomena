from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from .models import Room, RoomType


def room_list(request):
    rooms = Room.objects.filter(is_available=True).prefetch_related('images')

    # ── Filters ──────────────────────────────────────────
    room_type = request.GET.get('room_type', '')
    capacity  = request.GET.get('capacity',  '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by   = request.GET.get('sort',      'price_asc')

    if room_type:
        rooms = rooms.filter(room_type=room_type)
    if capacity:
        rooms = rooms.filter(capacity__gte=capacity)
    if min_price:
        rooms = rooms.filter(price_per_night__gte=min_price)
    if max_price:
        rooms = rooms.filter(price_per_night__lte=max_price)

    sort_options = {
        'price_asc':  'price_per_night',
        'price_desc': '-price_per_night',
        'capacity':   '-capacity',
        'name':       'name',
    }
    rooms = rooms.order_by(sort_options.get(sort_by, 'price_per_night'))

    context = {
        'rooms':      rooms,
        'room_types': RoomType.choices,
        'room_count': rooms.count(),
        'current_filters': {
            'room_type': room_type,
            'capacity':  capacity,
            'min_price': min_price,
            'max_price': max_price,
            'sort':      sort_by,
        },
    }
    return render(request, 'rooms/room_list.html', context)


def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk, is_available=True)

    # All images for the gallery
    images = room.images.all().order_by('order', 'id')

    # Other rooms to suggest at the bottom (same type, exclude current)
    related_rooms = Room.objects.filter(
        is_available=True
    ).exclude(pk=pk).prefetch_related('images')[:3]

    context = {
        'room':          room,
        'images':        images,
        'related_rooms': related_rooms,
    }
    return render(request, 'rooms/room_detail.html', context)