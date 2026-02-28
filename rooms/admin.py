from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Room, RoomImage


class RoomImageInline(admin.TabularInline):
    """
    Inline editor for room images —
    shown directly inside the Room admin page.
    """
    model        = RoomImage
    extra        = 3          # show 3 empty slots by default
    fields       = ('image', 'caption', 'is_main', 'order')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:80px; border-radius:4px;" />',
                obj.image.url
            )
        return _('No image yet')
    image_preview.short_description = _('Preview')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):

    # ── List view ───────────────────────────────────────
    list_display = (
        'name',
        'room_type',
        'price_per_night',
        'capacity',
        'is_available',
        'is_featured',
        'main_image_preview',
    )
    list_filter = (
        'room_type',
        'is_available',
        'is_featured',
        'has_balcony',
        'is_pet_friendly',
        'is_accessible',
    )
    search_fields = ('name', 'description')
    list_editable  = ('is_available', 'is_featured')
    list_per_page  = 20
    ordering       = ('room_type', 'price_per_night')

    # ── Detail view ─────────────────────────────────────
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'room_type', 'description')
        }),
        (_('Pricing & Capacity'), {
            'fields': ('price_per_night', 'capacity', 'size_sqm')
        }),
        (_('Room Details'), {
            'fields': ('bed_type', 'floor', 'view')
        }),
        (_('Amenities'), {
            'fields': (
                'has_balcony',
                'has_terrace',
                'has_air_con',
                'has_minibar',
                'has_safe',
                'has_bathrobe',
                'is_pet_friendly',
                'is_accessible',
                'is_non_smoking',
            ),
            'classes': ('collapse',),   # collapsible section
        }),
        (_('Visibility'), {
            'fields': ('is_available', 'is_featured')
        }),
    )

    inlines = [RoomImageInline]

    # ── Custom column: image thumbnail in list view ─────
    def main_image_preview(self, obj):
        img = obj.get_main_image()
        if img:
            return format_html(
                '<img src="{}" style="height:50px; border-radius:4px;" />',
                img.image.url
            )
        return _('No image')
    main_image_preview.short_description = _('Image')


@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display  = ('room', 'is_main', 'order', 'image_preview')
    list_filter   = ('room', 'is_main')
    list_editable = ('is_main', 'order')

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px; border-radius:4px;" />',
                obj.image.url
            )
        return _('No image')
    image_preview.short_description = _('Preview')