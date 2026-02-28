from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_booking_confirmation(booking):
    """
    Sends a confirmation email to the guest
    and a notification email to the hotel manager.
    """
    context = {
        'guest_name':    booking.guest_name,
        'reference':     booking.reference,
        'room_name':     booking.room.name,
        'check_in':      booking.check_in.strftime('%d %B %Y'),
        'check_out':     booking.check_out.strftime('%d %B %Y'),
        'nights':        booking.nights,
        'guests':        booking.guests,
        'price_per_night': booking.price_per_night,
        'total_price':   booking.total_price,
        'special_requests': booking.special_requests,
    }

    subject  = render_to_string(
        'bookings/emails/confirmation_subject.txt', context
    ).strip()
    body_txt  = render_to_string('bookings/emails/confirmation_body.txt',  context)
    body_html = render_to_string('bookings/emails/confirmation_body.html', context)

    # ── Email to guest ───────────────────────────────────
    guest_email = EmailMultiAlternatives(
        subject    = subject,
        body       = body_txt,
        from_email = settings.DEFAULT_FROM_EMAIL,
        to         = [booking.guest_email],
    )
    guest_email.attach_alternative(body_html, 'text/html')
    guest_email.send(fail_silently=False)

    # ── Notification to hotel manager ────────────────────
    manager_subject = f"[Nuova Prenotazione] {booking.reference} — {booking.guest_name}"
    manager_body    = (
        f"Nuova prenotazione ricevuta.\n\n"
        f"Riferimento : {booking.reference}\n"
        f"Ospite      : {booking.guest_name}\n"
        f"Email       : {booking.guest_email}\n"
        f"Telefono    : {booking.guest_phone}\n"
        f"Camera      : {booking.room.name}\n"
        f"Check-in    : {booking.check_in}\n"
        f"Check-out   : {booking.check_out}\n"
        f"Notti       : {booking.nights}\n"
        f"Ospiti      : {booking.guests}\n"
        f"Totale      : €{booking.total_price}\n"
    )
    if booking.special_requests:
        manager_body += f"Richieste    : {booking.special_requests}\n"

    manager_email = EmailMultiAlternatives(
        subject    = manager_subject,
        body       = manager_body,
        from_email = settings.DEFAULT_FROM_EMAIL,
        to         = [settings.MANAGER_EMAIL],
    )
    manager_email.send(fail_silently=True)