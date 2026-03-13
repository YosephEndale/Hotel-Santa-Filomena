from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, Count, Q
from .models import RoomBooking, TableBooking, BookingStatus


@staff_member_required
def admin_dashboard(request):
    today = timezone.now().date()
    now   = timezone.now()

    # ── Room Booking stats ────────────────────────────────
    checkins_today = RoomBooking.objects.filter(
        check_in=today,
        status__in=[BookingStatus.CONFIRMED, BookingStatus.PENDING]
    ).select_related('room').order_by('check_in')

    checkouts_today = RoomBooking.objects.filter(
        check_out=today,
        status__in=[BookingStatus.CONFIRMED, BookingStatus.COMPLETED]
    ).select_related('room').order_by('check_out')

    pending_room = RoomBooking.objects.filter(
        status=BookingStatus.PENDING
    ).select_related('room').order_by('check_in')

    upcoming_room = RoomBooking.objects.filter(
        check_in__gt=today,
        status=BookingStatus.CONFIRMED
    ).select_related('room').order_by('check_in')[:8]

    # Guests currently in-house
    inhouse = RoomBooking.objects.filter(
        check_in__lte=today,
        check_out__gt=today,
        status=BookingStatus.CONFIRMED
    ).select_related('room')

    # Revenue this month
    month_start = today.replace(day=1)
    revenue_month = RoomBooking.objects.filter(
        created_at__date__gte=month_start,
        status__in=[BookingStatus.CONFIRMED, BookingStatus.COMPLETED]
    ).aggregate(total=Sum('total_price'))['total'] or 0

    # ── Table Booking stats ───────────────────────────────
    tables_today = TableBooking.objects.filter(
        date=today,
        status__in=[BookingStatus.CONFIRMED, BookingStatus.PENDING]
    ).order_by('time_slot')

    pending_table = TableBooking.objects.filter(
        status=BookingStatus.PENDING
    ).order_by('date', 'time_slot')

    upcoming_table = TableBooking.objects.filter(
        date__gt=today,
        status=BookingStatus.CONFIRMED
    ).order_by('date', 'time_slot')[:8]

    # Covers tonight
    covers_tonight = TableBooking.objects.filter(
        date=today,
        time_slot__gte='19:00',
        status__in=[BookingStatus.CONFIRMED, BookingStatus.PENDING]
    ).aggregate(total=Sum('guests'))['total'] or 0

    covers_lunch = TableBooking.objects.filter(
        date=today,
        time_slot__lte='14:30',
        status__in=[BookingStatus.CONFIRMED, BookingStatus.PENDING]
    ).aggregate(total=Sum('guests'))['total'] or 0

    # ── Summary counts ────────────────────────────────────
    counts = {
        'checkins_today':   checkins_today.count(),
        'checkouts_today':  checkouts_today.count(),
        'inhouse':          inhouse.count(),
        'pending_room':     pending_room.count(),
        'tables_today':     tables_today.count(),
        'pending_table':    pending_table.count(),
        'covers_tonight':   covers_tonight,
        'covers_lunch':     covers_lunch,
        'revenue_month':    revenue_month,
    }

    context = {
        'title':            'Dashboard',
        'today':            today,
        'now':              now,
        'counts':           counts,
        'checkins_today':   checkins_today,
        'checkouts_today':  checkouts_today,
        'pending_room':     pending_room,
        'upcoming_room':    upcoming_room,
        'inhouse':          inhouse,
        'tables_today':     tables_today,
        'pending_table':    pending_table,
        'upcoming_table':   upcoming_table,
        # Pass through admin context
        'has_permission':   True,
    }
    return render(request, 'admin/dashboard.html', context)