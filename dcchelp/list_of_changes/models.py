from django.db import models


class SearchManager(models.Manager):
    """ Поиск по полям для SQLite"""
    def search(self, query):
        if not query:
            return self.none()

        results = self.filter(models.Q(title__iregex=query) | models.Q(text__iregex=query))
        return results


class Change(models.Model):
    """ Пункты листа изменений """
    STATUSES = (
        (True, 'Актуален'),
        (False, 'Отменен'),
    )

    number = models.IntegerField()
    title = models.CharField(max_length=255, verbose_name='Название')
    text = models.TextField(max_length=1000, verbose_name='Содержание')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated = models.DateTimeField(auto_now=True, verbose_name='Изменено')
    active = models.BooleanField(choices=STATUSES, default=STATUSES[0][0], verbose_name='Статус')
    link_approvement = models.CharField(blank=True, verbose_name='Ссылка на согласование')

    objects = models.Manager()
    search = SearchManager()

    class Meta:
        ordering = ['-number']
        verbose_name = 'Изменение'
        verbose_name_plural = 'Изменения'

    def __str__(self):
        return f'{self.number}. {self.title}'