from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import EmailTemplate


def _build_context(booking, booking_type='room'):
    """Build the shared template context for both booking types."""
    ctx = {
        'guest_name':       booking.guest_name,
        'guest_email':      booking.guest_email,
        'reference':        booking.reference,
        'guests':           booking.guests,
        'special_requests': booking.special_requests,
    }
    if booking_type == 'room':
        ctx.update({
            'room_name':      booking.room.name,
            'check_in':       booking.check_in.strftime('%d %B %Y'),
            'check_out':      booking.check_out.strftime('%d %B %Y'),
            'nights':         booking.nights,
            'price_per_night': booking.price_per_night,
            'total_price':    booking.total_price,
        })
    else:
        ctx.update({
            'date':      booking.date.strftime('%d %B %Y'),
            'time_slot': booking.time_slot,
            'service':   str(booking.service),
        })
    return ctx


def send_booking_confirmation(booking):
    context = _build_context(booking, 'room')

    # ── Try DB template first ─────────────────────────────
    db_template = EmailTemplate.get(EmailTemplate.TemplateKey.ROOM_CONFIRMATION)

    if db_template:
        subject  = db_template.render_subject(context)
        body_txt = db_template.render_body(context)
    else:
        # Fall back to file templates
        subject  = render_to_string(
            'bookings/emails/confirmation_subject.txt', context
        ).strip()
        body_txt = render_to_string(
            'bookings/emails/confirmation_body.txt', context
        )

    # HTML body always comes from the file template
    body_html = render_to_string(
        'bookings/emails/confirmation_body.html', context
    )

    # ── Email to guest ────────────────────────────────────
    guest_email = EmailMultiAlternatives(
        subject    = subject,
        body       = body_txt,
        from_email = settings.DEFAULT_FROM_EMAIL,
        to         = [booking.guest_email],
    )
    guest_email.attach_alternative(body_html, 'text/html')
    guest_email.send(fail_silently=False)

    # ── Notification to manager ───────────────────────────
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

    EmailMultiAlternatives(
        subject    = manager_subject,
        body       = manager_body,
        from_email = settings.DEFAULT_FROM_EMAIL,
        to         = [settings.MANAGER_EMAIL],
    ).send(fail_silently=True)


def send_table_confirmation(booking):
    context = _build_context(booking, 'table')

    # ── Try DB template first ─────────────────────────────
    db_template = EmailTemplate.get(EmailTemplate.TemplateKey.TABLE_CONFIRMATION)

    if db_template:
        subject  = db_template.render_subject(context)
        body_txt = db_template.render_body(context)
    else:
        subject  = render_to_string(
            'bookings/emails/table_confirmation_subject.txt', context
        ).strip()
        body_txt = render_to_string(
            'bookings/emails/table_confirmation_body.txt', context
        )

    body_html = render_to_string(
        'bookings/emails/table_confirmation_body.html', context
    )

    # ── Email to guest ────────────────────────────────────
    guest_email = EmailMultiAlternatives(
        subject    = subject,
        body       = body_txt,
        from_email = settings.DEFAULT_FROM_EMAIL,
        to         = [booking.guest_email],
    )
    guest_email.attach_alternative(body_html, 'text/html')
    guest_email.send(fail_silently=False)

    # ── Notification to manager ───────────────────────────
    manager_subject = f"[Nuovo Tavolo] {booking.reference} — {booking.guest_name}"
    manager_body    = (
        f"Nuova prenotazione tavolo.\n\n"
        f"Riferimento : {booking.reference}\n"
        f"Ospite      : {booking.guest_name}\n"
        f"Email       : {booking.guest_email}\n"
        f"Telefono    : {booking.guest_phone}\n"
        f"Data        : {booking.date}\n"
        f"Orario      : {booking.time_slot}\n"
        f"Servizio    : {booking.service}\n"
        f"Ospiti      : {booking.guests}\n"
    )
    if booking.special_requests:
        manager_body += f"Richieste    : {booking.special_requests}\n"

    EmailMultiAlternatives(
        subject    = manager_subject,
        body       = manager_body,
        from_email = settings.DEFAULT_FROM_EMAIL,
        to         = [settings.MANAGER_EMAIL],
    ).send(fail_silently=True)