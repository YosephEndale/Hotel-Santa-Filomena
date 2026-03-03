from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import MenuItem, MenuCategory


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):

    # ── List view ───────────────────────────────────────
    list_display = (
        'photo_preview',
        'name',
        'category',
        'price',
        'is_available',
        'is_featured',
        'is_signature',
        'is_seasonal',
        'order',
    )
    list_filter = (
        'category',
        'is_available',
        'is_featured',
        'is_signature',
        'is_vegetarian',
        'is_vegan',
        'is_gluten_free',
    )
    search_fields  = ('name', 'description')
    list_editable  = ('is_available', 'is_featured', 'order')
    list_per_page  = 30
    ordering       = ('category', 'order', 'name')

    # ── Group list by category ──────────────────────────
    list_display_links = ('name',)

    # ── Detail view ─────────────────────────────────────
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'category', 'description', 'price')
        }),
        (_('Photo'), {
            'fields': ('photo', 'photo_preview_detail')
        }),
        (_('Dietary Information'), {
            'fields': (
                'is_vegetarian',
                'is_vegan',
                'is_gluten_free',
            ),
            'classes': ('collapse',),
        }),
        (_('Visibility & Display'), {
            'fields': (
                'is_available',
                'is_featured',
                'is_signature',
                'is_seasonal',
                'order',
            )
        }),
    )

    readonly_fields = ('photo_preview_detail',)

    # ── Thumbnail in list view ──────────────────────────
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="height:55px; width:75px; '
                'object-fit:cover; border-radius:4px;" />',
                obj.photo.url
            )
        return '—'
    photo_preview.short_description = _('Photo')

    # ── Larger preview in detail view ──────────────────
    def photo_preview_detail(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height:200px; '
                'border-radius:6px; margin-top:8px;" />',
                obj.photo.url
            )
        return _('No photo uploaded yet')
    photo_preview_detail.short_description = _('Preview')