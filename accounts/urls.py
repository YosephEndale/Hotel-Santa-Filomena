from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/',  views.register,    name='register'),
    path('login/',     views.user_login,  name='login'),
    path('logout/',    views.user_logout, name='logout'),
    path('dashboard/', views.dashboard,   name='dashboard'),
    path('cancel/room/<str:reference>/',  views.cancel_room_booking,  name='cancel_room'),
    path('cancel/table/<str:reference>/', views.cancel_table_booking, name='cancel_table'),
]