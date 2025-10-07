from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('procedures/', views.procedures, name='procedures'),
    path('list_of_changes/', views.ListOfChangesView.as_view(), name='list_of_changes'),
    path('list_of_changes/add/', views.add_change, name='add_change'),
    path('change/<int:change_id>/edit/', views.edit_change, name='edit_change'),
    path('change/<int:change_id>/cancel/', views.cancel_change, name='cancel_change'),
    path('change/<int:change_id>/delete/', views.delete_change, name='delete_change'),
    path('documentation/', views.documentation, name='documentation'),
    path('documentation/content/<int:doc_type_id>/', views.get_documentation_content, name='documentation_type_content'),
    path('documentation/content/<int:doc_type_id>/<int:subtype_id>/', views.get_documentation_content, name='documentation_subtype_content'),
    path('documentation/add-article/', views.add_document_article, name='add_document_article'),
    path('documentation/get-subtypes/<int:doc_type_id>/', views.get_subtypes, name='get_subtypes'),
    path('processes/', views.processes, name='processes'),
    path('faq/', views.FAQView.as_view(), name='FAQ'),
    path('search/', views.search, name='search'),
]