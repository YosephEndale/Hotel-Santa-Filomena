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
class TimeSlot(models.TextChoices):
    LUNCH_1  = '12:30', _('12:30')
    LUNCH_2  = '13:00', _('13:00')
    LUNCH_3  = '13:30', _('13:30')
    LUNCH_4  = '14:00', _('14:00')
    DINNER_1 = '19:30', _('19:30')
    DINNER_2 = '20:00', _('20:00')
    DINNER_3 = '20:30', _('20:30')
    DINNER_4 = '21:00', _('21:00')
    DINNER_5 = '21:30', _('21:30')


class TableBooking(models.Model):

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

    # ── Reservation Details ─────────────────────────────
    date = models.DateField(
        _('Date')
    )
    time_slot = models.CharField(
        _('Time'),
        max_length=10,
        choices=TimeSlot.choices,
        default=TimeSlot.DINNER_1
    )
    guests = models.PositiveIntegerField(
        _('Number of Guests'),
        default=2
    )
    special_requests = models.TextField(
        _('Special Requests'),
        blank=True
    )

    # ── Status ──────────────────────────────────────────
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )

    # ── Reference ───────────────────────────────────────
    reference = models.CharField(
        _('Booking Reference'),
        max_length=20,
        unique=True,
        blank=True
    )

    # ── Timestamps ──────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Max seats per time slot across all tables
    MAX_SEATS_PER_SLOT = 30

    class Meta:
        verbose_name        = _('Table Booking')
        verbose_name_plural = _('Table Bookings')
        ordering            = ['-date', 'time_slot']

    def __str__(self):
        return f"{self.reference} — {self.guest_name} ({self.date} {self.time_slot})"

    # ── Computed properties ─────────────────────────────
    @property
    def is_upcoming(self):
        return self.date >= timezone.now().date()

    @property
    def service(self):
        """Returns 'Pranzo' or 'Cena' based on time slot."""
        if self.time_slot and self.time_slot <= '14:30':
            return _('Lunch')
        return _('Dinner')

    # ── Generate unique reference ───────────────────────
    def generate_reference(self):
        import random
        import string
        chars = string.ascii_uppercase + string.digits
        while True:
            ref = 'TB' + ''.join(random.choices(chars, k=8))
            if not TableBooking.objects.filter(reference=ref).exists():
                return ref

    # ── Seats taken for this slot ───────────────────────
    def seats_taken(self):
        """
        Total guests already booked for the same date + time slot.
        Excludes cancelled bookings and the current instance.
        """
        return TableBooking.objects.filter(
            date=self.date,
            time_slot=self.time_slot,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
        ).exclude(pk=self.pk).aggregate(
            total=models.Sum('guests')
        )['total'] or 0

    # ── Validation ──────────────────────────────────────
    def clean(self):
        if self.date and self.date < timezone.now().date():
            raise ValidationError(
                _('Reservation date cannot be in the past.')
            )

        # Monday = 0 in Python's weekday()
        if self.date and self.date.weekday() == 0:
            raise ValidationError(
                _('The restaurant is closed on Mondays.')
            )

        if self.guests and self.guests > 12:
            raise ValidationError(
                _('For groups larger than 12 please contact us directly.')
            )

        if self.date and self.time_slot and self.guests:
            available = self.MAX_SEATS_PER_SLOT - self.seats_taken()
            if self.guests > available:
                raise ValidationError(
                    _('Not enough seats available for this time slot. Please choose a different time.')
                )

    # ── Auto-fill reference on save ─────────────────────
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        super().save(*args, **kwargs)


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
        Only runs if room is already assigned to the instance.
        """
        try:
            room = self.room
        except Exception:
            # Room not assigned yet — skip conflict check
            return False

        return RoomBooking.objects.filter(
            room=room,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            check_in__lt=self.check_out,
            check_out__gt=self.check_in,
        ).exclude(pk=self.pk).exists()

    # ── Validation ──────────────────────────────────────
    def clean(self):
        # Only validate dates if both are present
        if self.check_in and self.check_out:
            if self.check_in >= self.check_out:
                raise ValidationError(
                    _('Check-out date must be after check-in date.')
                )
            if self.check_in < timezone.now().date():
                raise ValidationError(
                    _('Check-in date cannot be in the past.')
                )
            # Only check conflicts if room is assigned
            try:
                self.room
                if self.has_conflict():
                    raise ValidationError(
                        _('This room is not available for the selected dates.')
                    )
            except RoomBooking.room.RelatedObjectDoesNotExist:
                pass

    # ── Auto-fill price + reference on save ─────────────
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        if not self.price_per_night:
            self.price_per_night = self.room.price_per_night
        if not self.total_price:
            self.total_price = self.price_per_night * self.nights
        super().save(*args, **kwargs)


        