from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('room/', views.book_room, name='book_room'),
    path('table/', views.book_table, name='book_table'),
]