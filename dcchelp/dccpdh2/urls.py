from django.urls import path
from django_ckeditor_5.views import upload_file

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('faq/', views.FAQView.as_view(), name='FAQ'),
    path('search/', views.search, name='search'),
]