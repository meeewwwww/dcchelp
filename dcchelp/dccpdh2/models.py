from django.contrib.auth.models import User
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField(max_length=1000, blank=True, default='Ответа пока что нет...')
    answered = models.BooleanField(default=False)


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

'''
class Task(models.Model):
    ITERATIONS = (
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5')
    )

    STATUSES = (
        ('Не взята в работу', 'Не взята в работу'),
        ('Отработана', 'Отработана'),
        ('Возвращена на доработку', 'Возвращена на доработку'),
        ('ON HOLD', 'ON HOLD'),
        ('Cancelled', 'Cancelled'),
        ('Отозвана', 'Отозвана')
    )

    number = models.CharField(max_length=100, verbose_name='Номер заявки, PVA, TRM')
    created = models.DateTimeField(verbose_name='Время получения')
    name = models.CharField(max_length=100, verbose_name='Наименование комплекта')
    priority = models.BooleanField(default=False, verbose_name='Приоритет')
    iteration = models.IntegerField(choices=ITERATIONS, default=ITERATIONS[0][1], verbose_name='Итерация')
    status = models.CharField(max_length=50, choices=STATUSES, default=STATUSES[0][1])
    user = models.ForeignKey(User, verbose_name='Сотрудник ТДО', on_delete=models.DO_NOTHING)
    result = models.CharField(max_length=100, verbose_name='Созданный процесс, TRM', blank=True)
    comment = models.TextField(verbose_name='Комментарий', blank=True)
'''