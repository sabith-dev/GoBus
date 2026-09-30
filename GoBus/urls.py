from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('accounts.urls', namespace='accounts')),
    path('passenger/', include('passengers.urls', namespace='passengers')),
    path('agency/', include('agencies.urls', namespace='agencies')),
    path('buses/', include('buses.urls', namespace='buses')),
    path('routes/', include('routes.urls', namespace='routes')),
    path('schedules/', include('schedules.urls', namespace='schedules')),
    path('bookings/', include('bookings.urls', namespace='bookings')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('cancellations/', include('cancellations.urls', namespace='cancellations')),
    path('tracking/', include('tracking.urls', namespace='tracking')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('wallets/', include('wallets.urls', namespace='wallets')),
    path('referrals/', include('referrals.urls', namespace='referrals')),
    path('ai/', include('ai_assistant.urls', namespace='ai_assistant')),
    path('admin-portal/', include('dashboard.urls', namespace='admin_portal')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
