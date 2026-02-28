from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from rooms.models import Room


class BookingStatus(models.TextChoices):
    PENDING   = 'pending',   _('Pending')
    CONFIRMED = 'confirmed', _('Confirmed')
    CANCELLED = 'cancelled', _('Cancelled')
    COMPLETED = 'completed', _('Completed')


class RoomBooking(models.Model):

    # ── Room ────────────────────────────────────────────
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name=_('Room')
    )

    # ── Guest Info ──────────────────────────────────────
    guest_name = models.CharField(
        _('Full Name'),
        max_length=200
    )
    guest_email = models.EmailField(
        _('Email Address')
    )
    guest_phone = models.CharField(
        _('Phone Number'),
        max_length=30
    )

    # ── Stay Dates ──────────────────────────────────────
    check_in = models.DateField(
        _('Check-in Date')
    )
    check_out = models.DateField(
        _('Check-out Date')
    )
    guests = models.PositiveIntegerField(
        _('Number of Guests'),
        default=1
    )

    # ── Pricing (snapshot at time of booking) ───────────
    price_per_night = models.DecimalField(
        _('Price per Night'),
        max_digits=8,
        decimal_places=2
    )
    total_price = models.DecimalField(
        _('Total Price'),
        max_digits=10,
        decimal_places=2
    )

    # ── Status ──────────────────────────────────────────
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )

    # ── Extra ───────────────────────────────────────────
    special_requests = models.TextField(
        _('Special Requests'),
        blank=True
    )

    # ── Reference number ────────────────────────────────
    reference = models.CharField(
        _('Booking Reference'),
        max_length=20,
        unique=True,
        blank=True
    )

    # ── Timestamps ──────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = _('Room Booking')
        verbose_name_plural = _('Room Bookings')
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.reference} — {self.guest_name} ({self.check_in} → {self.check_out})"

    # ── Computed properties ─────────────────────────────
    @property
    def nights(self):
        return (self.check_out - self.check_in).days

    @property
    def is_upcoming(self):
        return self.check_in >= timezone.now().date()

    # ── Generate unique reference ───────────────────────
    def generate_reference(self):
        import random
        import string
        chars = string.ascii_uppercase + string.digits
        while True:
            ref = 'SF' + ''.join(random.choices(chars, k=8))
            if not RoomBooking.objects.filter(reference=ref).exists():
                return ref

    # ── Date conflict check ─────────────────────────────
    def has_conflict(self):
        """
        Returns True if another confirmed/pending booking
        overlaps the requested dates for the same room.
        """
        return RoomBooking.objects.filter(
            room=self.room,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            check_in__lt=self.check_out,
            check_out__gt=self.check_in,
        ).exclude(pk=self.pk).exists()

    # ── Validation ──────────────────────────────────────
    def clean(self):
        if self.check_in and self.check_out:
            if self.check_in >= self.check_out:
                raise ValidationError(
                    _('Check-out date must be after check-in date.')
                )
            if self.check_in < timezone.now().date():
                raise ValidationError(
                    _('Check-in date cannot be in the past.')
                )
            if self.has_conflict():
                raise ValidationError(
                    _('This room is not available for the selected dates.')
                )

    # ── Auto-fill price + reference on save ─────────────
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        if not self.price_per_night:
            self.price_per_night = self.room.price_per_night
        if not self.total_price:
            self.total_price = self.price_per_night * self.nights
        super().save(*args, **kwargs)