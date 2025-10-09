from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField(max_length=1000, blank=True, default='Ответа пока что нет...')
    answered = models.BooleanField(default=False)


class Change(models.Model):
    class Status(models.IntegerChoices):
        ACTIVE = 1, 'Актуален'
        CANCELLED = 0, 'Отменен'

    number = models.IntegerField()
    title = models.CharField(max_length=255, verbose_name='Название')
    text = models.TextField(max_length=1000, blank=True, verbose_name='Содержание')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated = models.DateTimeField(auto_now=True, verbose_name='Изменено')
    active = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
                                 default=Status.ACTIVE, verbose_name='Статус')
    link_approvement = models.URLField(blank=True, verbose_name='Ссылка на согласование')
    tags = models.ManyToManyField('Tag', related_name='change', blank=True, verbose_name='Теги') #возможно не будет использоваться - удалить

    class Meta:
        ordering = ['-number']
        verbose_name = 'Изменение'
        verbose_name_plural = 'Изменения'

    def __str__(self):
        return self.title


# Подумать над целесообразностью модели/раздела
class Procedure(models.Model):
    number = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.TextField(max_length=255)
    description = models.TextField(max_length=1000, blank=True)
    edms_link = models.URLField(blank=True)
    tags = models.ManyToManyField('Tag', related_name='procedure', blank=True)

    def __str__(self):
        return self.number


# Подумать над целесообразностью модели
class Tag(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})

    def __str__(self):
        return self.name


# Подумать над целесообразностью модели/раздела
class Process(models.Model):
    class Type(models.TextChoices):
        PVA = 'PVA-процесс'
        REVIEW = 'Review Transmittal'

    name = models.CharField(max_length=255)
    description = models.TextField(max_length=1000, blank=True)
    p_type = models.TextField(choices=Type.choices, default=Type.PVA)
    doc_types = models.ManyToManyField('DocumentTypes', related_name='processes', blank=True)


class DocumentTypes(models.Model):
    ru_name = models.CharField(max_length=255)
    en_name = models.CharField(max_length=255)
    ru_short = models.CharField(max_length=5)
    en_short = models.CharField(max_length=5)
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

#path('documentation/content/<int:doc_type_id>/<int:subtype_id>/', views.get_documentation_content, name='documentation_subtype_content'),
