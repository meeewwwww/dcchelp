from django.urls import path
from django_ckeditor_5.views import upload_file

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('procedures/', views.ProceduresView.as_view(), name='procedures'),
    path('documentation/', views.DocumentationView.as_view(), name='documentation'),
    path('documentation/content/<int:doc_type_id>/', views.get_documentation_content, name='documentation_type_content'),
    path('documentation/content/<int:doc_type_id>/<int:subtype_id>/', views.get_documentation_content, name='documentation_subtype_content'),
    path('documentation/add-article/', views.add_document_article, name='add_document_article'),
    path('upload/', upload_file, name='ck_editor_5_upload'),
    path('documentation/get-subtypes/<int:doc_type_id>/', views.get_subtypes, name='get_subtypes'),
    path('processes/', views.ProcessesView.as_view(), name='processes'),
    path('faq/', views.FAQView.as_view(), name='FAQ'),
    path('search/', views.search, name='search'),
]

