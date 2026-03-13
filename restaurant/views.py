from django.shortcuts import render
from .models import MenuItem, MenuCategory


def menu(request):
    items = MenuItem.objects.filter(is_available=True)

    menu_sections = []
    for value, label in MenuCategory.choices:
        section_items = items.filter(category=value).order_by('order', 'name')
        if section_items.exists():
            menu_sections.append({
                'category': value,
                'label':    label,
                'items':    section_items,
            })

    featured_items  = items.filter(is_featured=True)[:4]
    signature_items = items.filter(is_signature=True)[:3]

    context = {
        'menu_sections':   menu_sections,
        'featured_items':  featured_items,
        'signature_items': signature_items,
    }
    return render(request, 'restaurant/menu.html', context)