from django.urls import path

from . import views

urlpatterns = [
    path('list_of_changes/', views.ListOfChangesView.as_view(), name='list_of_changes'),
    path('list_of_changes/add/', views.add_change, name='add_change'),
    path('change/<int:change_id>/edit/', views.edit_change, name='edit_change'),
    path('change/<int:change_id>/cancel/', views.cancel_change, name='cancel_change'),
    path('change/<int:change_id>/delete/', views.delete_change, name='delete_change'),
    ]