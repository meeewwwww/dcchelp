from django.db import models


class Change(models.Model):
    class Status(models.IntegerChoices):
        ACTIVE = 1, 'Актуален'
        CANCELLED = 0, 'Отменен'

    number = models.IntegerField()
    title = models.CharField(max_length=255, verbose_name='Название')
    text = models.TextField(max_length=1000, verbose_name='Содержание')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated = models.DateTimeField(auto_now=True, verbose_name='Изменено')
    active = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
                                 default=Status.ACTIVE, verbose_name='Статус')
    link_approvement = models.CharField(blank=True, verbose_name='Ссылка на согласование')

    class Meta:
        ordering = ['-number']
        verbose_name = 'Изменение'
        verbose_name_plural = 'Изменения'

    def __str__(self):
        return self.title