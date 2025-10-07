"""
URL configuration for dcchelp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path, include
from dccpdh2.views import page_not_found


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dccpdh2.urls')),
] + debug_toolbar_urls()

handler404 = page_not_found
admin.site.site_header = 'Панель администрирования'
admin.site.index_title = 'DCC HELP PDH2'