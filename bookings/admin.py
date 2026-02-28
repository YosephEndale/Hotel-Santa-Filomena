from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import RoomBooking, BookingStatus


@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):

    list_display = (
        'reference',
        'guest_name',
        'guest_email',
        'room',
        'check_in',
        'check_out',
        'nights_display',
        'total_price',
        'status',
        'created_at',
    )
    list_filter  = ('status', 'room', 'check_in')
    search_fields = ('reference', 'guest_name', 'guest_email', 'guest_phone')
    list_editable = ('status',)
    readonly_fields = ('reference', 'price_per_night', 'total_price', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        (_('Booking Reference'), {
            'fields': ('reference', 'status')
        }),
        (_('Guest Information'), {
            'fields': ('guest_name', 'guest_email', 'guest_phone')
        }),
        (_('Stay Details'), {
            'fields': ('room', 'check_in', 'check_out', 'guests', 'special_requests')
        }),
        (_('Pricing'), {
            'fields': ('price_per_night', 'total_price')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def nights_display(self, obj):
        return f"{obj.nights} {_('nights')}"
    nights_display.short_description = _('Nights')

    def status_colored(self, obj):
        colors = {
            BookingStatus.PENDING:   '#f39c12',
            BookingStatus.CONFIRMED: '#2ecc71',
            BookingStatus.CANCELLED: '#e74c3c',
            BookingStatus.COMPLETED: '#95a5a6',
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="color:{}; font-weight:500;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = _('Status')