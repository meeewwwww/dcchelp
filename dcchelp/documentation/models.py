from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class DocumentTypes(models.Model):
    ru_name = models.CharField(max_length=255)
    en_name = models.CharField(max_length=255, blank=True, null=True)
    ru_short = models.CharField(max_length=5, blank=True, null=True)
    en_short = models.CharField(max_length=5, blank=True, null=True)
    sub_types = models.ManyToManyField('DocumentSubType', related_name='doc_types', blank=True)

    def __str__(self):
        return self.ru_name


class DocumentSubType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class DocumentArticle(models.Model):
    title = models.CharField(max_length=255)
    text = CKEditor5Field('Text', config_name='extends')
    doc_type = models.ForeignKey('DocumentTypes', on_delete=models.CASCADE, related_name='articles')
    doc_sub_type = models.ForeignKey('DocumentSubType', on_delete=models.CASCADE, related_name='articles')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"javascript:void(0)"  # или просто "#"

    def get_onclick(self):
        return f"loadSubtypeContent({self.doc_type_id}, {self.doc_sub_type_id})"