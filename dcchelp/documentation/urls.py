from django.urls import path
from . import views


urlpatterns = [
    path('', views.DocumentationView.as_view(), name='documentation'),
    path('content/<int:doc_type_id>/', views.get_documentation_content, name='documentation_type_content'),
    path('content/<int:doc_type_id>/<int:subtype_id>/', views.get_documentation_content, name='documentation_subtype_content'),
    path('add-article/', views.add_document_article, name='add_document_article'),
    path('article/<int:article_id>/edit/', views.edit_article, name='edit_article'),
    path('article/<int:article_id>/delete/', views.delete_article, name='delete_article'),
    path('get-subtypes/<int:doc_type_id>/', views.get_subtypes, name='get_subtypes'),
]
