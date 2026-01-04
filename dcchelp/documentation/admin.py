from django.contrib import admin

from .models import DocumentArticle, DocumentTypes, DocumentSubType


@admin.register(DocumentArticle)
class DocumentArticleAdmin(admin.ModelAdmin):
    ...


@admin.register(DocumentTypes)
class DocumentTypesAdmin(admin.ModelAdmin):
    ...


@admin.register(DocumentSubType)
class DocumentSubTypeAdmin(admin.ModelAdmin):
    ...