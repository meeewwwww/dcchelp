from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('faq/', views.FAQView.as_view(), name='FAQ'),
    path('search/', views.search, name='search'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]