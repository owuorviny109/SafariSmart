"""
URL configuration for safarismart project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('destinations/', include('destinations.urls')),
    path('accounts/', include('accounts.urls')),
    path('payments/', include('payments.urls')),
    path('api/', include('api.urls')),
]

# Serve media files - needed for updated images to show in production
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
