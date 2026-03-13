from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from bookings.admin_views import admin_dashboard

admin.site.site_header = 'Hotel Santa Filomena'
admin.site.site_title  = 'Santa Filomena Admin'
admin.site.index_title = 'Hotel Management'

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    # Admin dashboard — must come before admin/ 
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('rooms/', include('rooms.urls', namespace='rooms')),
    path('restaurant/', include('restaurant.urls', namespace='restaurant')),
    path('bookings/', include('bookings.urls', namespace='bookings')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)