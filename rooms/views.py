from django.shortcuts import render

def room_list(request):
    return render(request, 'rooms/room_list.html', {})