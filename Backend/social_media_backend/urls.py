from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/relationships/', include('relationships.urls')),
    path('api/messages/', include('direct_messages.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/search/', include('search.urls')),
    path('api/locations/', include('locations.urls')),
    path('api/events/', include('events.urls')),
    path('api/groups/', include('groups.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
