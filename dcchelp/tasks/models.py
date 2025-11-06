from collections import defaultdict
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib import admin
from django.db import models
from django.utils import timezone


class SearchManager(models.Manager):
    """ Поиск по полям для SQLite"""
    def search(self, query):
        if not query:
            return self.none()

        results = self.filter(models.Q(number__iregex=query) | models.Q(name__iregex=query) |
                              models.Q(result__iregex=query) | models.Q(comment__iregex=query))
        return results


class ActiveTaskManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status__in=['not_taken', 'in_progress', 'on_hold'])


class ActiveTaskChart72HoursManager(models.Manager):
    """ Кастомный Manager для возврата данных (тип: list) для дашборда на главной странице """
    def get_queryset(self):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)
        all_tasks = super().get_queryset().filter(created__date__gte=start_date)

        # Группируем задачи по дате создания
        tasks_by_date = defaultdict(int)
        for task in all_tasks:
            date_created = task.created.date()
            if date_created >= start_date:
                tasks_by_date[date_created] += 1

        # Заполняем все даты за последние 30 дней
        chart_data = []
        current_date = start_date
        while current_date <= end_date:
            chart_data.append({
                'date': current_date.strftime('%d.%m'),
                'count': tasks_by_date.get(current_date, 0)
            })
            current_date += timedelta(days=1)

        return chart_data


class Task(models.Model):
    """ Задачи, поступающие в ТДО - портал, ТРМ, отправка и т.д. в соответствии с TYPES_OF_TASK """
    ITERATIONS = (
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5')
    )

    STATUSES = (
        ('not_taken', 'Не взята в работу'),
        ('in_progress', 'В работе'),
        ('completed', 'Отработана'),
        ('returned', 'Возвращена на доработку'),
        ('on_hold', 'ON HOLD'),
        ('cancelled', 'Cancelled'),
        ('recalled', 'Отозвана'),
    )

    TYPES_OF_TASK = (
        ('portal', 'Портал'),
        ('sending', 'Отправка'),
        ('BBB', 'ВВВ 1С КФО'),
        ('TRMfromSPO', 'TRM от СПО'),
        ('SPOKVIP', 'СПО КВИП'),
        ('KMforRFQRFP', 'KM для RFQ/RFP'),
        ('approvement', 'Утверждающий проверки'),
    )

    number = models.CharField(max_length=100, verbose_name='Номер заявки, PVA, TRM')
    created = models.DateTimeField(verbose_name='Время получения')
    name = models.CharField(max_length=100, verbose_name='Наименование комплекта')
    type = models.CharField(max_length=50, choices=TYPES_OF_TASK, default=TYPES_OF_TASK[0][1], verbose_name='Тип')
    priority = models.BooleanField(default=False, verbose_name='Приоритет')
    iteration = models.IntegerField(choices=ITERATIONS, default=ITERATIONS[0][1], verbose_name='Итерация')
    status = models.CharField(max_length=50, choices=STATUSES, default=STATUSES[0][1], verbose_name='Статус')
    user = models.ForeignKey(get_user_model(), verbose_name='Сотрудник ТДО', on_delete=models.DO_NOTHING, null=True)
    finished = models.DateField(null=True, blank=True, verbose_name='Завершено')
    result = models.CharField(max_length=100, verbose_name='Созданный процесс, TRM', blank=True)
    comment = models.TextField(verbose_name='Комментарий', blank=True)

    objects = models.Manager()
    active_tasks = ActiveTaskManager()
    active_tasks_chart_72h = ActiveTaskChart72HoursManager()
    search = SearchManager()

    class Meta:
        ordering = ('-created', )
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return self.number

    @admin.display
    def created_date(self):
        return self.created.date