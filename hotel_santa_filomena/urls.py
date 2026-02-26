from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # Language switcher endpoint (must be outside i18n_patterns)
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('rooms/', include('rooms.urls', namespace='rooms')),
    path('restaurant/', include('restaurant.urls', namespace='restaurant')),
    path('bookings/', include('bookings.urls', namespace='bookings')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    prefix_default_language=False,  # Italian (default) has no prefix → /
                                    # English gets prefix → /en/
                                    # French gets prefix → /fr/
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)