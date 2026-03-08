from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
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
    from bookings.models import RoomBooking, TableBooking, BookingStatus
    today = timezone.now().date()
    email = request.user.email

    # ── Room bookings ─────────────────────────────────────
    all_room = RoomBooking.objects.filter(
        guest_email=email
    ).select_related('room').order_by('-check_in')

    upcoming_room = all_room.filter(
        check_in__gte=today
    ).exclude(status=BookingStatus.CANCELLED)

    past_room = all_room.filter(
        check_in__lt=today
    ) | all_room.filter(status=BookingStatus.CANCELLED)

    past_room = past_room.distinct().order_by('-check_in')

    # ── Table bookings ────────────────────────────────────
    all_table = TableBooking.objects.filter(
        guest_email=email
    ).order_by('-date')

    upcoming_table = all_table.filter(
        date__gte=today
    ).exclude(status=BookingStatus.CANCELLED)

    past_table = all_table.filter(
        date__lt=today
    ) | all_table.filter(status=BookingStatus.CANCELLED)

    past_table = past_table.distinct().order_by('-date')

    # ── Stats ─────────────────────────────────────────────
    stats = {
        'total_room_bookings':  all_room.count(),
        'total_table_bookings': all_table.count(),
        'upcoming_stays':       upcoming_room.count(),
        'upcoming_dinners':     upcoming_table.count(),
    }

    context = {
        'upcoming_room':  upcoming_room,
        'past_room':      past_room,
        'upcoming_table': upcoming_table,
        'past_table':     past_table,
        'stats':          stats,
        'today':          today,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def cancel_room_booking(request, reference):
    from bookings.models import RoomBooking, BookingStatus
    booking = get_object_or_404(
        RoomBooking,
        reference=reference,
        guest_email=request.user.email
    )

    if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
        messages.error(request, _('This booking cannot be cancelled.'))
        return redirect('accounts:dashboard')

    if booking.check_in <= timezone.now().date():
        messages.error(request, _('Cannot cancel a booking that has already started or passed.'))
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        booking.status = BookingStatus.CANCELLED
        booking.save()
        messages.success(
            request,
            _('Booking %(ref)s has been cancelled.') % {'ref': booking.reference}
        )
        return redirect('accounts:dashboard')

    return render(request, 'accounts/cancel_confirm.html', {
        'booking': booking,
        'type':    'room',
    })


@login_required
def cancel_table_booking(request, reference):
    from bookings.models import TableBooking, BookingStatus
    booking = get_object_or_404(
        TableBooking,
        reference=reference,
        guest_email=request.user.email
    )

    if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
        messages.error(request, _('This reservation cannot be cancelled.'))
        return redirect('accounts:dashboard')

    if booking.date <= timezone.now().date():
        messages.error(request, _('Cannot cancel a reservation for today or a past date.'))
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        booking.status = BookingStatus.CANCELLED
        booking.save()
        messages.success(
            request,
            _('Reservation %(ref)s has been cancelled.') % {'ref': booking.reference}
        )
        return redirect('accounts:dashboard')

    return render(request, 'accounts/cancel_confirm.html', {
        'booking': booking,
        'type':    'table',
    })