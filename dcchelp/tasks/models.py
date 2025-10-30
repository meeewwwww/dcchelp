from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models


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
        ('not_taken', 'Не взята в работу'),
        ('in_progress', 'В работе'),
        ('completed', 'Отработана'),
        ('returned', 'Возвращена на доработку'),
        ('on_hold', 'ON HOLD'),
        ('cancelled', 'Cancelled'),
        ('recalled', 'Отозвана'),
    )

    number = models.CharField(max_length=100, verbose_name='Номер заявки, PVA, TRM')
    created = models.DateTimeField(verbose_name='Время получения')
    name = models.CharField(max_length=100, verbose_name='Наименование комплекта')
    priority = models.BooleanField(default=False, verbose_name='Приоритет')
    iteration = models.IntegerField(choices=ITERATIONS, default=ITERATIONS[0][1], verbose_name='Итерация')
    status = models.CharField(max_length=50, choices=STATUSES, default=STATUSES[0][1])
    user = models.ForeignKey(get_user_model(), verbose_name='Сотрудник ТДО', on_delete=models.DO_NOTHING)
    result = models.CharField(max_length=100, verbose_name='Созданный процесс, TRM', blank=True)
    comment = models.TextField(verbose_name='Комментарий', blank=True)