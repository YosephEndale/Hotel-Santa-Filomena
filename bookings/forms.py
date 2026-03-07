from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import RoomBooking, BookingStatus, TimeSlot, TableBooking
from django.db import models

class RoomBookingForm(forms.ModelForm):

    class Meta:
        model  = RoomBooking
        fields = [
            'guest_name',
            'guest_email',
            'guest_phone',
            'check_in',
            'check_out',
            'guests',
            'special_requests',
        ]
        widgets = {
            'guest_name': forms.TextInput(attrs={
                'class':       'booking-form__input',
                'placeholder': _('Mario Rossi'),
            }),
            'guest_email': forms.EmailInput(attrs={
                'class':       'booking-form__input',
                'placeholder': _('mario@example.com'),
            }),
            'guest_phone': forms.TextInput(attrs={
                'class':       'booking-form__input',
                'placeholder': _('+39 06 1234 5678'),
            }),
            'check_in': forms.DateInput(attrs={
                'class': 'booking-form__input',
                'type':  'date',
            }),
            'check_out': forms.DateInput(attrs={
                'class': 'booking-form__input',
                'type':  'date',
            }),
            'guests': forms.NumberInput(attrs={
                'class': 'booking-form__input',
                'min':   '1',
            }),
            'special_requests': forms.Textarea(attrs={
                'class':       'booking-form__input',
                'rows':        3,
                'placeholder': _('Any special requests or notes for your stay...'),
            }),
        }
        labels = {
            'guest_name':        _('Full Name'),
            'guest_email':       _('Email Address'),
            'guest_phone':       _('Phone Number'),
            'check_in':          _('Check-in Date'),
            'check_out':         _('Check-out Date'),
            'guests':            _('Number of Guests'),
            'special_requests':  _('Special Requests'),
        }

    def __init__(self, *args, room=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.room = room

        # Pre-fill dates from GET params if passed
        if room:
            self.fields['guests'].widget.attrs['max'] = room.capacity

        # Mark required fields
        for field in ['guest_name', 'guest_email', 'guest_phone', 'check_in', 'check_out']:
            self.fields[field].required = True

        self.fields['special_requests'].required = False

    def clean_check_in(self):
        check_in = self.cleaned_data.get('check_in')
        if check_in and check_in < timezone.now().date():
            raise forms.ValidationError(_('Check-in date cannot be in the past.'))
        return check_in

    def clean_check_out(self):
        check_out = self.cleaned_data.get('check_out')
        return check_out

    def clean(self):
        cleaned = super().clean()
        check_in  = cleaned.get('check_in')
        check_out = cleaned.get('check_out')
        guests    = cleaned.get('guests')

        if check_in and check_out:
            if check_out <= check_in:
                raise forms.ValidationError(
                    _('Check-out date must be after check-in date.')
                )

        if self.room and guests:
            if guests > self.room.capacity:
                raise forms.ValidationError(
                    _('Number of guests exceeds room capacity.')
                )

        # Check date conflicts
        if self.room and check_in and check_out:
            from .models import BookingStatus
            conflict = RoomBooking.objects.filter(
                room=self.room,
                status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
                check_in__lt=check_out,
                check_out__gt=check_in,
            ).exists()
            if conflict:
                raise forms.ValidationError(
                    _('This room is not available for the selected dates. Please choose different dates.')
                )

        return cleaned


class TableBookingForm(forms.ModelForm):

    class Meta:
        model  = TableBooking
        fields = [
            'guest_name',
            'guest_email',
            'guest_phone',
            'date',
            'time_slot',
            'guests',
            'special_requests',
        ]
        widgets = {
            'guest_name': forms.TextInput(attrs={
                'class':       'booking-form__input',
                'placeholder': _('Mario Rossi'),
            }),
            'guest_email': forms.EmailInput(attrs={
                'class':       'booking-form__input',
                'placeholder': _('mario@example.com'),
            }),
            'guest_phone': forms.TextInput(attrs={
                'class':       'booking-form__input',
                'placeholder': _('+39 06 1234 5678'),
            }),
            'date': forms.DateInput(attrs={
                'class': 'booking-form__input',
                'type':  'date',
            }),
            'time_slot': forms.Select(attrs={
                'class': 'booking-form__input',
            }),
            'guests': forms.NumberInput(attrs={
                'class': 'booking-form__input',
                'min':   '1',
                'max':   '12',
            }),
            'special_requests': forms.Textarea(attrs={
                'class':       'booking-form__input',
                'rows':        3,
                'placeholder': _('Allergies, celebrations, seating preferences...'),
            }),
        }
        labels = {
            'guest_name':       _('Full Name'),
            'guest_email':      _('Email Address'),
            'guest_phone':      _('Phone Number'),
            'date':             _('Date'),
            'time_slot':        _('Time'),
            'guests':           _('Number of Guests'),
            'special_requests': _('Special Requests'),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if not date:
            return date
        if date < timezone.now().date():
            raise forms.ValidationError(
                _('Reservation date cannot be in the past.')
            )
        if date.weekday() == 0:
            raise forms.ValidationError(
                _('The restaurant is closed on Mondays.')
            )
        return date

    def clean_guests(self):
        guests = self.cleaned_data.get('guests')
        if guests and guests > 12:
            raise forms.ValidationError(
                _('For groups larger than 12 please contact us directly.')
            )
        return guests

    def clean(self):
        cleaned   = super().clean()
        date      = cleaned.get('date')
        time_slot = cleaned.get('time_slot')
        guests    = cleaned.get('guests')

        if date and time_slot and guests:
            # Check seat availability
            from .models import TableBooking as TB
            seats_taken = TB.objects.filter(
                date=date,
                time_slot=time_slot,
                status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            ).aggregate(
                total=models.Sum('guests')
            )['total'] or 0

            available = TableBooking.MAX_SEATS_PER_SLOT - seats_taken
            if guests > available:
                raise forms.ValidationError(
                    _('Not enough seats available for this time slot. Please choose a different time.')
                )
        return cleaned