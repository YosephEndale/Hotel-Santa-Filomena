from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('rooms/', include('rooms.urls', namespace='rooms')),
    path('restaurant/', include('restaurant.urls', namespace='restaurant')),
    path('bookings/', include('bookings.urls', namespace='bookings')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)