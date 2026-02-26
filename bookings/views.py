from django.shortcuts import render

def book_room(request):
    return render(request, 'bookings/book_room.html', {})

def book_table(request):
    return render(request, 'bookings/book_table.html', {})