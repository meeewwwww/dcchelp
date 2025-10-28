from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from dccpdh2.views import page_not_found


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dccpdh2.urls')),
    path('', include('list_of_changes.urls')),
] + debug_toolbar_urls()

handler404 = page_not_found
admin.site.site_header = 'Панель администрирования'
admin.site.index_title = 'DCC HELP PDH2'

urlpatterns += [
    path("ckeditor5/", include('django_ckeditor_5.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
