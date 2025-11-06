from bs4 import BeautifulSoup
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class SearchManager(models.Manager):
    """ Поиск по полям для SQLite"""
    def search(self, query):
        if not query:
            return self.none()

        results = self.filter(models.Q(title__iregex=query) | models.Q(clean_text__iregex=query))
        return results


class DocumentArticle(models.Model):
    """ Заметки о документации, для сохранения скриншотов используется Base64 - не требует отдельного каталога media.
    CKeditor для поля text используется без подписки - с ограниченным функционалом """
    title = models.CharField(max_length=255)
    text = CKEditor5Field('Text', config_name='extends')
    clean_text = models.TextField(blank=True)
    doc_type = models.ForeignKey('DocumentTypes', on_delete=models.CASCADE, related_name='articles')
    doc_sub_type = models.ForeignKey('DocumentSubType', on_delete=models.CASCADE, related_name='articles')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    search = SearchManager()

    class Meta:
        verbose_name = 'Заметка о документации'
        verbose_name_plural = 'Заметки о документации'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Автоматически генерируем clean_text при сохранении
        if self.text:
            self.clean_text = self.html_to_text(self.text)
        super().save(*args, **kwargs)

    @staticmethod
    def html_to_text(html_content):
        if not html_content:
            return ""
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text(strip=True)

    @staticmethod
    def get_absolute_url():
        return "#"

    def get_onclick(self):
        return f"loadSubtypeContent({self.doc_type_id}, {self.doc_sub_type_id})"


class DocumentTypes(models.Model):
    """ Типы документации / заметок о документации """
    ru_name = models.CharField(max_length=255)
    sub_types = models.ManyToManyField('DocumentSubType', related_name='doc_types', blank=True)

    class Meta:
        ordering = ('ru_name', )
        verbose_name = 'Тип документа / заметки'
        verbose_name_plural = 'Типы документов / заметки'

    def __str__(self):
        return self.ru_name


class DocumentSubType(models.Model):
    """ Подтипы документации / заметок о документации """
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name', )
        verbose_name = 'Подтип документа / заметки'
        verbose_name_plural = 'Подтипы документов / заметки'

    def __str__(self):
        return self.name