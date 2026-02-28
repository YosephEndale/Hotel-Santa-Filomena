from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

class RoomType(models.TextChoices):
    CAMERA_SINGOLA     = 'singola',     _('Camera Singola')      # Single room
    CAMERA_DOPPIA      = 'doppia',      _('Camera Doppia')       # Double room (twin beds)
    CAMERA_MATRIMONIALE = 'matrimoniale', _('Camera Matrimoniale') # Double room (one bed)
    JUNIOR_SUITE       = 'junior_suite', _('Junior Suite')       # Junior Suite
    SUITE_PANORAMICA   = 'panoramica',  _('Suite Panoramica')    # Panoramic Suite
    CASALE             = 'casale',      _('Casale')              # Private farmhouse cottage


class Room(models.Model):
    # ── Basic Info ──────────────────────────────────────
    name = models.CharField(
        _('Name'),
        max_length=200
    )
    room_type = models.CharField(
        _('Room Type'),
        max_length=20,
        choices=RoomType.choices,
        default=RoomType.CAMERA_SINGOLA
    )
    description = models.TextField(
        _('Description')
    )

    # ── Pricing ─────────────────────────────────────────
    price_per_night = models.DecimalField(
        _('Price per Night'),
        max_digits=8,
        decimal_places=2
    )

    # ── Capacity ────────────────────────────────────────
    capacity = models.PositiveIntegerField(
        _('Capacity (guests)'),
        default=2
    )

    # ── Features ────────────────────────────────────────
    size_sqm = models.PositiveIntegerField(
        _('Room Size (m²)'),
        null=True,
        blank=True
    )
    bed_type = models.CharField(
        _('Bed Type'),
        max_length=100,
        blank=True
    )
    floor = models.PositiveIntegerField(
        _('Floor'),
        null=True,
        blank=True
    )
    view = models.CharField(
        _('View'),
        max_length=100,
        blank=True
    )

    # ── Amenities (booleans) ────────────────────────────
    has_balcony        = models.BooleanField(_('Balcony'),          default=False)
    has_terrace        = models.BooleanField(_('Terrace'),          default=False)
    has_air_con        = models.BooleanField(_('Air Conditioning'), default=True)
    has_minibar        = models.BooleanField(_('Mini Bar'),         default=False)
    has_safe           = models.BooleanField(_('Safe'),             default=True)
    has_bathrobe       = models.BooleanField(_('Bathrobe'),         default=False)
    is_pet_friendly    = models.BooleanField(_('Pet Friendly'),     default=False)
    is_accessible      = models.BooleanField(_('Accessible'),       default=False)
    is_non_smoking     = models.BooleanField(_('Non Smoking'),      default=True)

    # ── Availability & Visibility ───────────────────────
    is_available = models.BooleanField(
        _('Available for Booking'),
        default=True
    )
    is_featured = models.BooleanField(
        _('Featured on Homepage'),
        default=False
    )

    # ── Timestamps ──────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = _('Room')
        verbose_name_plural = _('Rooms')
        ordering            = ['room_type', 'price_per_night']

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"

    def get_main_image(self):
        """Returns the first image or None."""
        return self.images.filter(is_main=True).first() or self.images.first()
    
def get_absolute_url(self):
    return reverse('rooms:room_detail', kwargs={'pk': self.pk})


class RoomImage(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Room')
    )
    image = models.ImageField(
        _('Image'),
        upload_to='rooms/'
    )
    caption = models.CharField(
        _('Caption'),
        max_length=200,
        blank=True
    )
    is_main = models.BooleanField(
        _('Main Image'),
        default=False
    )
    order = models.PositiveIntegerField(
        _('Display Order'),
        default=0
    )

    class Meta:
        verbose_name        = _('Room Image')
        verbose_name_plural = _('Room Images')
        ordering            = ['order', 'id']

    def __str__(self):
        return f"{self.room.name} — image {self.id}"
    

    