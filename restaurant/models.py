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