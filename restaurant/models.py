from django.db import models
from django.utils.translation import gettext_lazy as _


class MenuCategory(models.TextChoices):
    STARTER  = 'starter',  _('Antipasti')
    PASTA    = 'pasta',    _('Primi Piatti')
    MAIN     = 'main',     _('Secondi Piatti')
    SIDE     = 'side',     _('Contorni')
    DESSERT  = 'dessert',  _('Dolci')
    DRINK    = 'drink',    _('Bevande')
    WINE     = 'wine',     _('Vini')


class MenuItem(models.Model):

    # ── Basic Info ──────────────────────────────────────
    name = models.CharField(
        _('Name'),
        max_length=200
    )
    category = models.CharField(
        _('Category'),
        max_length=20,
        choices=MenuCategory.choices,
        default=MenuCategory.STARTER
    )
    description = models.TextField(
        _('Description'),
        blank=True
    )

    # ── Pricing ─────────────────────────────────────────
    price = models.DecimalField(
        _('Price'),
        max_digits=7,
        decimal_places=2
    )

    # ── Photo ───────────────────────────────────────────
    photo = models.ImageField(
        _('Photo'),
        upload_to='menu/',
        null=True,
        blank=True
    )

    # ── Dietary flags ───────────────────────────────────
    is_vegetarian  = models.BooleanField(_('Vegetarian'),    default=False)
    is_vegan       = models.BooleanField(_('Vegan'),         default=False)
    is_gluten_free = models.BooleanField(_('Gluten Free'),   default=False)
    is_signature   = models.BooleanField(_('Signature Dish'), default=False)
    is_seasonal    = models.BooleanField(_('Seasonal'),      default=False)

    # ── Availability & Visibility ───────────────────────
    is_available = models.BooleanField(
        _('Available'),
        default=True
    )
    is_featured = models.BooleanField(
        _('Featured on Homepage'),
        default=False
    )

    # ── Display order within category ───────────────────
    order = models.PositiveIntegerField(
        _('Display Order'),
        default=0
    )

    # ── Timestamps ──────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = _('Menu Item')
        verbose_name_plural = _('Menu Items')
        ordering            = ['category', 'order', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()}) — €{self.price}"
    
class RestaurantSettings(models.Model):
    """
    Singleton model — only one row should ever exist.
    Controls opening hours and closed days shown on the website.
    """

    # ── Lunch service ────────────────────────────────────
    lunch_open  = models.TimeField(
        _('Lunch Opening Time'),
        default='12:30'
    )
    lunch_close = models.TimeField(
        _('Lunch Closing Time'),
        default='14:30'
    )
    lunch_enabled = models.BooleanField(
        _('Lunch Service Active'),
        default=True
    )

    # ── Dinner service ───────────────────────────────────
    dinner_open  = models.TimeField(
        _('Dinner Opening Time'),
        default='19:30'
    )
    dinner_close = models.TimeField(
        _('Dinner Closing Time'),
        default='22:30'
    )
    dinner_enabled = models.BooleanField(
        _('Dinner Service Active'),
        default=True
    )

    # ── Closed days ──────────────────────────────────────
    closed_monday    = models.BooleanField(_('Closed Monday'),    default=True)
    closed_tuesday   = models.BooleanField(_('Closed Tuesday'),   default=False)
    closed_wednesday = models.BooleanField(_('Closed Wednesday'), default=False)
    closed_thursday  = models.BooleanField(_('Closed Thursday'),  default=False)
    closed_friday    = models.BooleanField(_('Closed Friday'),    default=False)
    closed_saturday  = models.BooleanField(_('Closed Saturday'),  default=False)
    closed_sunday    = models.BooleanField(_('Closed Sunday'),    default=False)

    # ── Extra note (shown on site) ───────────────────────
    closed_note = models.CharField(
        _('Closing Note'),
        max_length=120,
        blank=True,
        help_text=_('Optional note shown under hours, e.g. "Closed in August"')
    )

    class Meta:
        verbose_name        = _('Restaurant Settings')
        verbose_name_plural = _('Restaurant Settings')

    def __str__(self):
        return 'Restaurant Settings'

    # ── Singleton: always return the same row ─────────────
    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    # ── Helper: list of closed day names ─────────────────
    def closed_days(self):
        days = []
        mapping = [
            ('closed_monday',    _('Monday')),
            ('closed_tuesday',   _('Tuesday')),
            ('closed_wednesday', _('Wednesday')),
            ('closed_thursday',  _('Thursday')),
            ('closed_friday',    _('Friday')),
            ('closed_saturday',  _('Saturday')),
            ('closed_sunday',    _('Sunday')),
        ]
        for field, label in mapping:
            if getattr(self, field):
                days.append(str(label))
        return days

    # ── Helper: format time as HH:MM ─────────────────────
    def fmt(self, t):
        return t.strftime('%H:%M') if t else ''