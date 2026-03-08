from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import RegisterForm, LoginForm


def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                _('Welcome to Hotel Santa Filomena, %(name)s!') % {
                    'name': user.first_name or user.username
                }
            )
            return redirect('core:home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(
                request,
                _('Welcome back, %(name)s!') % {
                    'name': user.first_name or user.username
                }
            )
            # Redirect to next or home
            redirect_to = request.POST.get('next') or next_url or 'core:home'
            return redirect(redirect_to)
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {
        'form':     form,
        'next_url': next_url,
    })


def user_logout(request):
    logout(request)
    messages.info(request, _('You have been logged out. See you soon!'))
    return redirect('core:home')


@login_required
def dashboard(request):
    from bookings.models import RoomBooking, TableBooking
    room_bookings  = RoomBooking.objects.filter(
        guest_email=request.user.email
    ).order_by('-created_at')[:5]
    table_bookings = TableBooking.objects.filter(
        guest_email=request.user.email
    ).order_by('-created_at')[:5]

    return render(request, 'accounts/dashboard.html', {
        'room_bookings':  room_bookings,
        'table_bookings': table_bookings,
    })