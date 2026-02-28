from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from rooms.models import Room
from .models import RoomBooking
from .forms import RoomBookingForm
from .emails import send_booking_confirmation


def book_room(request):
    # Pre-select room from query param (comes from room detail/listing page)
    room_id = request.GET.get('room') or request.POST.get('room')
    room    = get_object_or_404(Room, pk=room_id, is_available=True) if room_id else None

    # Pre-fill dates from query params
    initial = {}
    if request.GET.get('check_in'):
        initial['check_in'] = request.GET.get('check_in')
    if request.GET.get('check_out'):
        initial['check_out'] = request.GET.get('check_out')
    if request.GET.get('guests'):
        initial['guests'] = request.GET.get('guests')

    if request.method == 'POST':
        form = RoomBookingForm(request.POST, room=room)

        if form.is_valid():
            booking          = form.save(commit=False)
            booking.room     = room
            booking.price_per_night = room.price_per_night
            booking.total_price     = booking.price_per_night * booking.nights
            booking.save()

            # Send confirmation email
            try:
                send_booking_confirmation(booking)
            except Exception:
                # Don't block confirmation if email fails
                pass

            return redirect('bookings:booking_confirmation', reference=booking.reference)

    else:
        form = RoomBookingForm(initial=initial, room=room)

    # All available rooms for the room selector
    available_rooms = Room.objects.filter(is_available=True)

    context = {
        'form':            form,
        'room':            room,
        'available_rooms': available_rooms,
    }
    return render(request, 'bookings/book_room.html', context)


def booking_confirmation(request, reference):
    booking = get_object_or_404(RoomBooking, reference=reference)
    return render(request, 'bookings/booking_confirmation.html', {'booking': booking})


def book_table(request):
    return render(request, 'bookings/book_table.html', {})