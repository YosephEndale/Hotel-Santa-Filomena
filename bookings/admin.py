from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Sum, Count
from .models import RoomBooking, TableBooking, BookingStatus


# ── Inline status actions ────────────────────────────────────
def confirm_bookings(modeladmin, request, queryset):
    updated = queryset.exclude(
        status=BookingStatus.CANCELLED
    ).update(status=BookingStatus.CONFIRMED)
    modeladmin.message_user(
        request,
        _('%(n)s booking(s) marked as Confirmed.') % {'n': updated}
    )
confirm_bookings.short_description = _('Mark selected as Confirmed')


def cancel_bookings(modeladmin, request, queryset):
    updated = queryset.exclude(
        status=BookingStatus.COMPLETED
    ).update(status=BookingStatus.CANCELLED)
    modeladmin.message_user(
        request,
        _('%(n)s booking(s) marked as Cancelled.') % {'n': updated}
    )
cancel_bookings.short_description = _('Mark selected as Cancelled')


def complete_bookings(modeladmin, request, queryset):
    updated = queryset.filter(
        status=BookingStatus.CONFIRMED
    ).update(status=BookingStatus.COMPLETED)
    modeladmin.message_user(
        request,
        _('%(n)s booking(s) marked as Completed.') % {'n': updated}
    )
complete_bookings.short_description = _('Mark selected as Completed')


# ── Filters ──────────────────────────────────────────────────
class UpcomingFilter(admin.SimpleListFilter):
    title        = _('Period')
    parameter_name = 'period'

    def lookups(self, request, model_admin):
        return [
            ('upcoming',  _('Upcoming')),
            ('today',     _('Check-in Today')),
            ('this_week', _('This Week')),
            ('past',      _('Past')),
        ]

    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == 'upcoming':
            return queryset.filter(check_in__gte=today)
        if self.value() == 'today':
            return queryset.filter(check_in=today)
        if self.value() == 'this_week':
            week_end = today + timezone.timedelta(days=7)
            return queryset.filter(check_in__gte=today, check_in__lte=week_end)
        if self.value() == 'past':
            return queryset.filter(check_in__lt=today)
        return queryset


# ══════════════════════════════════════════════════════════════
#   ROOM BOOKING ADMIN
# ══════════════════════════════════════════════════════════════
@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):

    # ── List view ────────────────────────────────────────────
    list_display = (
        'reference',
        'status_badge',
        'guest_name',
        'guest_email',
        'room_link',
        'check_in',
        'check_out',
        'nights_display',
        'guests',
        'slot_capacity',
        'total_price_display',
        'created_at_display',
    )
    list_filter = (
        'status',
        UpcomingFilter,
        'room',
        'check_in',
    )
    search_fields = (
        'reference',
        'guest_name',
        'guest_email',
        'guest_phone',
        'room__name',
    )
    list_per_page      = 25
    ordering           = ('-check_in',)
    date_hierarchy     = 'check_in'
    actions            = [confirm_bookings, cancel_bookings, complete_bookings]
    list_display_links = ('reference', 'guest_name')
    show_full_result_count = True

    # ── Detail view ──────────────────────────────────────────
    readonly_fields = (
        'reference',
        'price_per_night',
        'total_price',
        'nights_display',
        'created_at',
        'updated_at',
        'booking_summary_panel',
    )

    fieldsets = (
        (None, {
            'fields': ('booking_summary_panel',)
        }),
        (_('Status'), {
            'fields': ('status',),
        }),
        (_('Guest Information'), {
            'fields': (
                'guest_name',
                'guest_email',
                'guest_phone',
            ),
        }),
        (_('Stay Details'), {
            'fields': (
                'room',
                'check_in',
                'check_out',
                'nights_display',
                'guests',
                'special_requests',
            ),
        }),
        (_('Pricing'), {
            'fields': (
                'price_per_night',
                'total_price',
            ),
        }),
        (_('System'), {
            'fields': ('reference', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # ── Custom columns ───────────────────────────────────────
    def status_badge(self, obj):
        colors = {
            BookingStatus.PENDING:   ('#f39c12', '#fff8ee'),
            BookingStatus.CONFIRMED: ('#2ecc71', '#eefff5'),
            BookingStatus.CANCELLED: ('#e74c3c', '#fff0ee'),
            BookingStatus.COMPLETED: ('#95a5a6', '#f5f5f5'),
        }
        color, bg = colors.get(obj.status, ('#000', '#fff'))
        return format_html(
            '<span style="'
            'display:inline-block;'
            'padding:3px 10px;'
            'border-radius:2px;'
            'border:1px solid {};'
            'background:{};'
            'color:{};'
            'font-size:11px;'
            'font-weight:500;'
            'letter-spacing:0.05em;'
            'white-space:nowrap;'
            '">{}</span>',
            color, bg, color,
            obj.get_status_display()
        )
    status_badge.short_description = _('Status')
    status_badge.admin_order_field = 'status'

    def room_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:rooms_room_change', args=[obj.room.pk])
        return format_html('<a href="{}">{}</a>', url, obj.room.name)
    room_link.short_description = _('Room')
    room_link.admin_order_field = 'room__name'

    def nights_display(self, obj):
        return f"{obj.nights} {'night' if obj.nights == 1 else 'nights'}"
    nights_display.short_description = _('Nights')

    def total_price_display(self, obj):
        return format_html(
            '<strong style="color:#C9A96E;">€{}</strong>',
            obj.total_price
        )
    total_price_display.short_description = _('Total')
    total_price_display.admin_order_field = 'total_price'

    def created_at_display(self, obj):
        return obj.created_at.strftime('%d %b %Y, %H:%M')
    created_at_display.short_description = _('Booked At')
    created_at_display.admin_order_field = 'created_at'

    def booking_summary_panel(self, obj):
        if not obj.pk:
            return '—'
        status_colors = {
            BookingStatus.PENDING:   '#f39c12',
            BookingStatus.CONFIRMED: '#2ecc71',
            BookingStatus.CANCELLED: '#e74c3c',
            BookingStatus.COMPLETED: '#95a5a6',
        }
        color = status_colors.get(obj.status, '#666')
        return format_html(
            '''
            <div style="
              background:#1A1612;
              color:#FAF7F2;
              padding:1.5rem 2rem;
              border-left:4px solid {status_color};
              font-family:Georgia,serif;
              margin-bottom:0.5rem;
            ">
              <div style="font-size:11px;letter-spacing:0.3em;
                          text-transform:uppercase;color:#C9A96E;
                          margin-bottom:0.4rem;">
                Booking Reference
              </div>
              <div style="font-size:1.6rem;font-weight:300;
                          margin-bottom:1rem;">
                {reference}
              </div>
              <div style="display:flex;gap:3rem;flex-wrap:wrap;
                          font-family:sans-serif;font-size:13px;">
                <div>
                  <div style="color:#8A7F74;font-size:11px;
                              text-transform:uppercase;letter-spacing:0.15em;
                              margin-bottom:2px;">Guest</div>
                  <div>{guest_name}</div>
                  <div style="color:#8A7F74;font-size:12px;">{guest_email}</div>
                </div>
                <div>
                  <div style="color:#8A7F74;font-size:11px;
                              text-transform:uppercase;letter-spacing:0.15em;
                              margin-bottom:2px;">Room</div>
                  <div>{room}</div>
                </div>
                <div>
                  <div style="color:#8A7F74;font-size:11px;
                              text-transform:uppercase;letter-spacing:0.15em;
                              margin-bottom:2px;">Stay</div>
                  <div>{check_in} → {check_out}</div>
                  <div style="color:#8A7F74;font-size:12px;">
                    {nights} · {guests} guests
                  </div>
                </div>
                <div>
                  <div style="color:#8A7F74;font-size:11px;
                              text-transform:uppercase;letter-spacing:0.15em;
                              margin-bottom:2px;">Total</div>
                  <div style="color:#C9A96E;font-size:1.3rem;">
                    €{total}
                  </div>
                </div>
              </div>
            </div>
            ''',
            status_color = color,
            reference    = obj.reference,
            guest_name   = obj.guest_name,
            guest_email  = obj.guest_email,
            room         = obj.room.name,
            check_in     = obj.check_in.strftime('%d %b %Y'),
            check_out    = obj.check_out.strftime('%d %b %Y'),
            nights       = f"{obj.nights} nights",
            guests       = obj.guests,
            total        = obj.total_price,
        )
    booking_summary_panel.short_description = _('Booking Summary')

    def slot_capacity(self, obj):
        from .models import BookingStatus
        seats_taken = TableBooking.objects.filter(
            date=obj.date,
            time_slot=obj.time_slot,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
        ).aggregate(
            total=__import__('django.db.models', fromlist=['Sum']).Sum('guests')
        )['total'] or 0

        capacity  = TableBooking.MAX_SEATS_PER_SLOT
        remaining = capacity - seats_taken
        pct       = int((seats_taken / capacity) * 100)

        # Colour: green under 60%, amber 60–85%, red over 85%
        if pct < 60:
            color = '#2ecc71'
        elif pct < 85:
            color = '#f39c12'
        else:
            color = '#e74c3c'

        return format_html(
            '<span style="font-size:11px;color:{};">'
            '{}/{} seats'
            '</span>',
            color,
            seats_taken,
            capacity,
        )
    slot_capacity.short_description = _('Slot Capacity')

# ══════════════════════════════════════════════════════════════
#   TABLE BOOKING ADMIN
# ══════════════════════════════════════════════════════════════
class TableUpcomingFilter(admin.SimpleListFilter):
    title          = _('Period')
    parameter_name = 'period'

    def lookups(self, request, model_admin):
        return [
            ('upcoming',  _('Upcoming')),
            ('today',     _('Today')),
            ('this_week', _('This Week')),
            ('past',      _('Past')),
        ]

    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == 'upcoming':
            return queryset.filter(date__gte=today)
        if self.value() == 'today':
            return queryset.filter(date=today)
        if self.value() == 'this_week':
            week_end = today + timezone.timedelta(days=7)
            return queryset.filter(date__gte=today, date__lte=week_end)
        if self.value() == 'past':
            return queryset.filter(date__lt=today)
        return queryset


def confirm_table_bookings(modeladmin, request, queryset):
    updated = queryset.exclude(
        status=BookingStatus.CANCELLED
    ).update(status=BookingStatus.CONFIRMED)
    modeladmin.message_user(
        request,
        _('%(n)s reservation(s) marked as Confirmed.') % {'n': updated}
    )
confirm_table_bookings.short_description = _('Mark selected as Confirmed')


def cancel_table_bookings(modeladmin, request, queryset):
    updated = queryset.exclude(
        status=BookingStatus.COMPLETED
    ).update(status=BookingStatus.CANCELLED)
    modeladmin.message_user(
        request,
        _('%(n)s reservation(s) marked as Cancelled.') % {'n': updated}
    )
cancel_table_bookings.short_description = _('Mark selected as Cancelled')


@admin.register(TableBooking)
class TableBookingAdmin(admin.ModelAdmin):

    list_display = (
        'reference',
        'status_badge',
        'guest_name',
        'guest_email',
        'date',
        'time_slot',
        'service_display',
        'guests',
        'created_at_display',
    )
    list_filter = (
        'status',
        TableUpcomingFilter,
        'time_slot',
        'date',
    )
    search_fields = (
        'reference',
        'guest_name',
        'guest_email',
        'guest_phone',
    )
    list_per_page      = 25
    ordering           = ('-date', 'time_slot')
    date_hierarchy     = 'date'
    actions            = [confirm_table_bookings, cancel_table_bookings]
    list_display_links = ('reference', 'guest_name')

    readonly_fields = (
        'reference',
        'created_at',
        'updated_at',
        'table_summary_panel',
    )

    fieldsets = (
        (None, {
            'fields': ('table_summary_panel',)
        }),
        (_('Status'), {
            'fields': ('status',),
        }),
        (_('Guest Information'), {
            'fields': (
                'guest_name',
                'guest_email',
                'guest_phone',
            ),
        }),
        (_('Reservation Details'), {
            'fields': (
                'date',
                'time_slot',
                'guests',
                'special_requests',
            ),
        }),
        (_('System'), {
            'fields': ('reference', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        colors = {
            BookingStatus.PENDING:   ('#f39c12', '#fff8ee'),
            BookingStatus.CONFIRMED: ('#2ecc71', '#eefff5'),
            BookingStatus.CANCELLED: ('#e74c3c', '#fff0ee'),
            BookingStatus.COMPLETED: ('#95a5a6', '#f5f5f5'),
        }
        color, bg = colors.get(obj.status, ('#000', '#fff'))
        return format_html(
            '<span style="'
            'display:inline-block;'
            'padding:3px 10px;'
            'border-radius:2px;'
            'border:1px solid {};'
            'background:{};'
            'color:{};'
            'font-size:11px;'
            'font-weight:500;'
            'letter-spacing:0.05em;'
            'white-space:nowrap;'
            '">{}</span>',
            color, bg, color,
            obj.get_status_display()
        )
    status_badge.short_description = _('Status')
    status_badge.admin_order_field = 'status'

    def service_display(self, obj):
        icon = '🌞' if obj.time_slot <= '14:30' else '🌙'
        return format_html('{} {}', icon, obj.service)
    service_display.short_description = _('Service')

    def created_at_display(self, obj):
        return obj.created_at.strftime('%d %b %Y, %H:%M')
    created_at_display.short_description = _('Booked At')
    created_at_display.admin_order_field = 'created_at'

    def table_summary_panel(self, obj):
        if not obj.pk:
            return '—'
        status_colors = {
            BookingStatus.PENDING:   '#f39c12',
            BookingStatus.CONFIRMED: '#2ecc71',
            BookingStatus.CANCELLED: '#e74c3c',
            BookingStatus.COMPLETED: '#95a5a6',
        }
        color = status_colors.get(obj.status, '#666')
        return format_html(
            '''
            <div style="
              background:#1A1612;
              color:#FAF7F2;
              padding:1.5rem 2rem;
              border-left:4px solid {status_color};
              font-family:Georgia,serif;
              margin-bottom:0.5rem;
            ">
              <div style="font-size:11px;letter-spacing:0.3em;
                          text-transform:uppercase;color:#C9A96E;
                          margin-bottom:0.4rem;">
                Table Reservation
              </div>
              <div style="font-size:1.6rem;font-weight:300;
                          margin-bottom:1rem;">
                {reference}
              </div>
              <div style="display:flex;gap:3rem;flex-wrap:wrap;
                          font-family:sans-serif;font-size:13px;">
                <div>
                  <div style="color:#8A7F74;font-size:11px;
                              text-transform:uppercase;letter-spacing:0.15em;
                              margin-bottom:2px;">Guest</div>
                  <div>{guest_name}</div>
                  <div style="color:#8A7F74;font-size:12px;">{guest_email}</div>
                </div>
                <div>
                  <div style="color:#8A7F74;font-size:11px;
                              text-transform:uppercase;letter-spacing:0.15em;
                              margin-bottom:2px;">Date & Time</div>
                  <div>{date} at {time_slot}</div>
                  <div style="color:#8A7F74;font-size:12px;">{service}</div>
                </div>
                <div>
                  <div style="color:#8A7F74;font-size:11px;
                              text-transform:uppercase;letter-spacing:0.15em;
                              margin-bottom:2px;">Guests</div>
                  <div style="color:#C9A96E;font-size:1.3rem;">
                    {guests}
                  </div>
                </div>
              </div>
            </div>
            ''',
            status_color = color,
            reference    = obj.reference,
            guest_name   = obj.guest_name,
            guest_email  = obj.guest_email,
            date         = obj.date.strftime('%d %b %Y'),
            time_slot    = obj.time_slot,
            service      = obj.service,
            guests       = obj.guests,
        )
    table_summary_panel.short_description = _('Reservation Summary')